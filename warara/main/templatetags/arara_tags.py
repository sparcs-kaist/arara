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
