from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import arara
import warara

def index(request):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    ret, board_list = server.board_manager.get_board_list()
    assert ret, board_list
    r['board_list'] = board_list

    rendered = render_to_string('sysop/index.html', r)
    return HttpResponse(rendered)

def add_board(request):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    ret, msg = server.board_manager.add_board(sess, request.POST['add_board_name'], request.POST['add_board_description'])
    assert ret, msg
    return HttpResponseRedirect('/sysop/')

def remove_board(request):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    ret, board_list = server.board_manager.get_board_list()
    assert ret, board_list
    for board in board_list:
        if request.POST.get(board['board_name'], None):
            ret, msg = server.board_manager.delete_board(sess, board['board_name'])
            assert ret, msg
    return HttpResponseRedirect('/sysop/')

def confirm_user(request):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    ret, msg = server.sysop_manager.conform_username_valusernameation(sess, request.POST['confirm_username'])
    assert ret, msg
    return HttpResponseRedirect('/sysop/')
