#-*- coding: utf-8 -*-
import arara
from django import template
from django.core.cache import cache
register = template.Library()

@register.tag(name="get_board_list")
def do_get_board_list(parser, token):
    return BoardListUpdateNode()

class BoardListUpdateNode(template.Node):
    def render(self, context):
        server = arara.get_server() 

        board_list = cache.get('board_list')
        if not board_list:
            board_list = server.board_manager.get_board_list()
            cache.set('board_list', board_list, 600)
        context["board_list"] = board_list
        return ""

@register.filter(name='get_board_description')
def do_get_board_description(value, arg):
    "Get board name and board description"
    server = arara.get_server()
    board_description = cache.get('board_description.' + value)
    if not board_description:
        board_description = server.board_manager.get_board(value).board_description
        cache.set('board_description.' + value, board_description, 600)
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
