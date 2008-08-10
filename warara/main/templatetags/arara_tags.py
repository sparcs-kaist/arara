import arara
from django import template
register = template.Library()

@register.tag(name="get_board_list")
def do_get_board_list(parser, token):
    return BoardListUpdateNode()

class BoardListUpdateNode(template.Node):
    def render(self, context):
        server = arara.get_server() 
        ret, board_list = server.board_manager.get_board_list()
        context["board_list"] = board_list
        return ""
