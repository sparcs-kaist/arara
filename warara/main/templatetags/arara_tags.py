#-*- coding: utf-8 -*-
import time
import datetime
from warara import warara_middleware
from arara_thrift.ttypes import NotLoggedIn
from django import template
from django.core.cache import cache
from django.utils.dateformat import format as _format
from etc import warara_settings
register = template.Library()

WEATHER_ICON_PATH = '/media/image/weather/'
WEATHER_ICON_SET = [
    # weather view grep first string and replace it to second string
    ('chance_of_snow.gif', '13.png'),
    ('flurries.gif', '14.png'),
    ('snow.gif', '15.png'),
    ('sleet.gif', '10.png'),
    ('chance_of_rain.gif', '9.png'),
    ('chance_of_storm.gif', '9.png'),
    ('showers.gif', '11.png'),
    ('mist.gif', '2.png'),
    ('rain.gif', '2.png'),
    ('storm.gif', '12.png'),
    ('thunderstorm.gif', '4.png'),
    ('rain_snow.gif', '10.png'),
    ('sunny.gif', '32.png'),
    ('partly_cloudy.gif', '30.png'),
    ('mostly_cloudy.gif', '28.png'),
    ('cloudy.gif', '26.png'),
    ('fog.gif', '20.png'),
    ('smoke.gif', '22.png'),
    ('haze.gif', '21.png'),
    ('dust.gif', '19.png'),
    ('icy.gif', '25.png'),
]

#CACHETIME_BOARD_LIST = 600
CACHETIME_BOARD_LIST = 6
#CACHETIME_BOARD_DESCRIPTION = 600
CACHETIME_BOARD_DESCRIPTION = 6
CACHETIME_BOARD_ALIAS = 6

@register.tag(name="get_board_list")
def do_get_board_list(parser, token):
    return BoardListUpdateNode()

class BoardListUpdateNode(template.Node):
    def render(self, context):
        server = warara_middleware.get_server() 

        board_list = cache.get('board_list')
        if not board_list:
            # hide 속성이 걸려 있지 않은 게시판만 표시한다.
            # TODO: hide 된 보드도 모두 Web 상으로 보고 싶은 유저가 있을 수 있다!
            board_list = filter(lambda x: not x.hide, server.board_manager.get_board_list())
            cache.set('board_list', board_list, CACHETIME_BOARD_LIST)
        context["board_list"] = board_list

        category1_list = []
        category2_list = []
        category3_list = []
        category4_list = []
        category5_list = []
        category6_list = []
        for board in board_list:
            if(board.category_id==1):
                category1_list+=[board]
            elif (board.category_id==2):
                category2_list.append(board)
            elif (board.category_id==3):
                category3_list.append(board)
            elif (board.category_id==4):
                category4_list.append(board)
            elif (board.category_id==5):
                category5_list.append(board)
            elif (board.category_id==6):
                category6_list.append(board)
            else:
                pass
        context['category1_list'] = category1_list
        context['category2_list'] = category2_list
        context['category3_list'] = category3_list
        context['category4_list'] = category4_list
        context['category5_list'] = category5_list
        context['category6_list'] = category6_list

        return ""

@register.tag(name="get_selected_boards")
def do_get_selected_boards(parser, token):
    return SelectedBoardsNode()

class SelectedBoardsNode(template.Node):
    def render(self, context):
        server = warara_middleware.get_server()
        if context.get('logged_in'):
            selected_boards = [(x.board_alias, x.board_name) for x in server.member_manager.get_selected_boards(context['arara_session'])]
        else:
            selected_boards = warara_settings.DEFAULT_MOBILE_BOARDS
        if len(selected_boards) == 0:
            selected_boards = warara_settings.DEFAULT_MOBILE_BOARDS

        context['selected_boards'] = selected_boards[:3]

        return ""

@register.tag(name="get_weather_info")
def do_get_weather_info(parser, token):
    return WeatherInfoNode()

class WeatherInfoNode(template.Node):
    def render(self, ctx):
        server = warara_middleware.get_server()
        # XXX(hodduc) : wairara.check_logged_in을 거쳤음에도 불구하고 Context를 따로 만들어서 쓰는 view가 너무 많다.
        # 하나로 통일하는 것이 깔끔해 보인다
        if not 'arara_session' in ctx:
            return ''
        sess = ctx['arara_session']
        # Get Weather info
        if warara_settings.USE_WEATHER_FORECAST:
            ctx['weather_info'] = server.bot_manager.get_weather_info(sess)
            if ctx['weather_info'].city == None:
                ctx['has_weather'] = False
            else:
                if ctx['weather_info'].city.lower() == 'daejeon':
                    ctx['weather_info'].city = u'대전'
                elif ctx['weather_info'].city.lower() == 'seoul':
                    ctx['weather_info'].city = u'서울'

                ctx['weather_info'].current_icon_url = weather_icon_replace(ctx['weather_info'].current_icon_url)
                ctx['weather_info'].tomorrow_icon_url = weather_icon_replace(ctx['weather_info'].tomorrow_icon_url)
                ctx['weather_info'].day_after_tomorrow_icon_url = weather_icon_replace(ctx['weather_info'].day_after_tomorrow_icon_url)
                ctx['has_weather'] = True
        else:
            ctx['has_weather'] = False

        return ""

@register.tag(name="get_notification")
def do_get_notification(parser, token):
    offset, length = token.split_contents()[1:3]
    return NotiNode(offset, length)

class NotiNode(template.Node):
    def __init__(self, offset, length):
        self.offset = int(offset)
        self.length = int(length)

    def render(self, ctx):
        server = warara_middleware.get_server()
        if not 'arara_session' in ctx:
            return ''
        sess = ctx['arara_session']

        try:
            ctx['noti'] = server.noti_manager.get_noti(sess, self.offset, self.length)
            ctx['unread_noti_count'] = sum(1 if not n.read else 0 for n in ctx['noti'])
        except NotLoggedIn:
            pass

        return ''

def weather_icon_replace(orig_url):
    # google의 icon을 아라 디자인에 맞는 weather icon으로 converting 하는 함수
    for source, dest in WEATHER_ICON_SET:
        if orig_url.endswith(source):
            return WEATHER_ICON_PATH + dest
    # 만약 아라에 적절한 아이콘이 없을 경우 앞에 http://www.google.com을 붙여 줌(기본 아이콘 사용)
    return "http://www.google.com" + orig_url


@register.filter(name='get_board_description')
def do_get_board_description(value, arg):
    "Get board name and board description"
    server = warara_middleware.get_server()
    board_description = cache.get('board_description.' + value)
    if not board_description:
        board_description = server.board_manager.get_board(value).board_description
        cache.set('board_description.' + value, board_description, CACHETIME_BOARD_DESCRIPTION)
    return board_description

@register.filter(name='get_board_alias')
def do_get_board_alias(value):
    "Get board name and board alias"
    server = warara_middleware.get_server()
    board_alias = cache.get('board_alias.' + value)
    if not board_alias:
        board_alias = server.board_manager.get_board(value).board_alias
        cache.set('board_alias.' + value, board_alias, CACHETIME_BOARD_ALIAS)
    return board_alias

@register.filter(name='truncatechars')
def do_truncatechars(value, arg):
    length = None
    if isinstance(arg, str) or isinstance(arg, unicode):
        length = int(arg)
    if not isinstance(length, int):
        return value # die silently
    if isinstance(value, str):
        value = unicode(value, 'utf-8') # XXX: use settings.DEFAULT_CHARSET
    if not isinstance(value, unicode):
        return value # die silently

    lensum = 0
    i = 0
    for i in range(len(value)):
        if u'가' < value[i] < u'힣':
            lensum += 2
        elif u'ㄱ' < value[i] < u'ㅎ':
            lensum += 2
        elif u'ㅏ'< value[i] < u'ㅣ':
            lensum += 2
        else:
            lensum += 1
        if lensum > length:
            break
    if i==len(value)-1:
        pass
    else:
        value = value[:i] + '...'
    return value

@register.filter(name='date_relative')
def do_date_relative(value):
    """
    Args:
        value: Timestamp, seconds

    Returns:
        Relative datetime string if seconds <= weeks, or M/D type date string.
    """

    def create_time_string(seconds):
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        days = hours / 24

        if days > 0:
            return u"{0}일 전".format(days)
        elif hours > 0:
            return u"{0}시간 전".format(hours)
        elif minutes > 0:
            return u"{0}분 전".format(minutes)
        else:
            return u"방금"

    then = int(value)
    now = int(time.mktime(time.localtime()))

    if now - then > 604800:  # weeks
        return _format(datetime.datetime.fromtimestamp(value), 'm/d')

    return create_time_string(now - then)
