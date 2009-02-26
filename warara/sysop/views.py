from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import arara
import warara

def index(request):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    board_list = server.board_manager.get_board_list()
    r['board_list'] = board_list

    rendered = render_to_string('sysop/index.html', r)
    return HttpResponse(rendered)

def add_board(request):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    msg = server.board_manager.add_board(sess, request.POST['add_board_name'], request.POST['add_board_description'])
    return HttpResponseRedirect('/sysop/')

def remove_board(request):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    board_list = server.board_manager.get_board_list()
    for board in board_list:
        if request.POST.get(board['board_name'], None):
            msg = server.board_manager.delete_board(sess, board['board_name'])
    return HttpResponseRedirect('/sysop/')

def confirm_user(request):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    msg = server.member_manager.backdoor_confirm(sess, request.POST['confirm_username'])
    return HttpResponseRedirect('/sysop/')

def wrap_error(f):
    def check_error(*args, **argv):
        r = {} #render item
        try:
            return f(*args, **argv)
        except StandardError, e:
            if e.message == "NOT_LOGGED_IN":
                r['error_message'] = e.message
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)
            elif e.message == "arara_session_key":
                r['error_message'] = "NOT_LOGGED_IN"
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)
            else:
                rendered = render_to_string("error.html")
                return HttpResponse(rendered)

    return check_error

#index = wrap_error(index)
#add_board = wrap_error(add_board)
#remove_board = wrap_error(remove_board)
#confirm_user = wrap_error(confirm_user)
