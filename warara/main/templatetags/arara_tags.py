#-*- coding: utf-8 -*-
from warara import warara_middleware
from django import template
from django.core.cache import cache
from etc.warara_settings import USE_WEATHER_FORECAST, WEATHER_ICON_PATH, WEATHER_ICON_SET
register = template.Library()

#CACHETIME_BOARD_LIST = 600
CACHETIME_BOARD_LIST = 6
#CACHETIME_BOARD_DESCRIPTION = 600
CACHETIME_BOARD_DESCRIPTION = 6

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
            else:
                print "no category\n"
        context['category1_list'] = category1_list
        context['category2_list'] = category2_list
        context['category3_list'] = category3_list
        context['category4_list'] = category4_list
        context['category5_list'] = category5_list

        return ""

@register.tag(name="get_weather_info")
def do_get_weather_info(parser, token):
    return WeatherInfoNode()

class WeatherInfoNode(template.Node):
    def render(self, ctx):
        server = warara_middleware.get_server()
        # XXX(hodduc) : wairara.check_logged_in을 거쳤음에도 불구하고 Context를 따로 만들어서 쓰는 view가 너무 많다.
        # 하나로 통일하는 것이 깔끔해 보인다
        if not ctx.has_key('arara_session'):
            return ''
        sess = ctx['arara_session']
        # Get Weather info
        if USE_WEATHER_FORECAST:
            ctx['weather_info'] = server.bot_manager.get_weather_info(sess)
            if ctx['weather_info'].city == None:
                ctx['has_weather'] = False
            else:
                if ctx['weather_info'].city.lower() == 'daejeon':
                    ctx['weather_info'].city = u'대전'
                elif ctx['weather_info'].city.lower == 'seoul':
                    ctx['weather_info'].city = u'서울'

                ctx['weather_info'].current_icon_url = weather_icon_replace(ctx['weather_info'].current_icon_url)
                ctx['weather_info'].tomorrow_icon_url = weather_icon_replace(ctx['weather_info'].tomorrow_icon_url)
                ctx['weather_info'].day_after_tomorrow_icon_url = weather_icon_replace(ctx['weather_info'].day_after_tomorrow_icon_url)
                ctx['has_weather'] = True
        else:
            ctx['has_weather'] = False

        return ""

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
