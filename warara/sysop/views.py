from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import warara
from warara import warara_middleware

@warara.wrap_error
def index(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    board_list = server.board_manager.get_board_list()
    r['board_list'] = board_list

    rendered = render_to_string('sysop/index.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def add_board(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    server.board_manager.add_board(sess, request.POST['add_board_name'], request.POST['add_board_description'])
    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def remove_board(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    board_list = server.board_manager.get_board_list()
    for board in board_list:
        if request.POST.get(board.board_name, None):
            msg = server.board_manager.delete_board(sess, board.board_name)
    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def confirm_user(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    msg = server.member_manager.backdoor_confirm(sess, request.POST['confirm_username'])
    return HttpResponseRedirect('/sysop/')
