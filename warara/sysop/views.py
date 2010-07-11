#-*- coding: utf-8 -*-
import datetime
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import warara
from warara import warara_middleware

from arara.util import datetime2timestamp

@warara.wrap_error
def index(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    board_list = server.board_manager.get_board_list()
    r['board_list'] = board_list

    # TODO: 배너를 단순히 나열하기보다는 배너의 날짜 등을 함께 표시하는 것이 어떨까?
    banner_list = server.notice_manager.list_banner(sess)
    r['banner_list'] = banner_list

    rendered = render_to_string('sysop/index.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def add_board(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    # 말머리도 적어넣었구나
    board_headings = []
    headings_string = request.POST.get('add_board_headings', None)
    if headings_string:
        #TODO: 중복 검사 등
        #TODO: 공백 말머리는 허용하지 말 것
        board_headings = [x.strip() for x in headings_string.split(",")]

    server.board_manager.add_board(sess, request.POST['add_board_name'], request.POST['add_board_description'], board_headings)
    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def modify_boards(request):
    '''
    선택된 보드들을 삭제 / 숨김 / 숨김 해제한다.
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    board_list = server.board_manager.get_board_list()
    # 어떤 명령을 주었는지 확인한다.
    action = None
    if request.POST.get('remove', None) != None:
        action = 'remove'
    elif request.POST.get('hide', None) != None:
        action = 'hide'
    elif request.POST.get('return_hide', None) != None:
        action = 'return_hide'
    else:
        raise InvalidOperation("unknown_sysop_board_modification_command")
    # 주어진 명령을 선택된 모든 보드에 대하여 시행한다.
    for board in board_list:
        if request.POST.get(board.board_name, None):
            if action == 'remove':
                msg = server.board_manager.delete_board(sess, board.board_name)
            elif action == 'hide':
                msg = server.board_manager.hide_board(sess, board.board_name)
            elif action == 'return_hide':
                msg = server.board_manager.return_hide_board(sess, board.board_name)
            # 그 밖의 경우는 위에서 필터링되므로 신경쓰지 않는다.
    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def edit_board(request):
    '''
    지정한 이름의 게시판의 이름 자체나 설명을 바꾼다.
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    original_board_name = request.POST['orig_board_name']
    new_board_name = request.POST['new_board_name']
    new_board_description = request.POST['new_board_description']
    server.board_manager.edit_board(sess, original_board_name, new_board_name, new_board_description)
    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def confirm_user(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    msg = server.member_manager.backdoor_confirm(sess, request.POST['confirm_username'])
    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def hide_board(request):
    """
    request 에 주어진 hide_board_name 의 보드를 숨긴다.
    """
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    board_list = server.board_manager.get_board_list()
    for board in board_list:
        if request.POST.get(board.board_name, None):
            msg = server.board_manager.hide_board(sess, board.board_name)
    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def return_hide_board(request):
    """
    request 에 주어진 hide_board_name 의 보드의 숨김을 해제한다.
    """
    # TODO: 나중에 관련 함수 이름 전체를 unhide 같은 것으로 바꾸자.
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    board_list = server.board_manager.get_board_list()
    for board in board_list:
        if request.POST.get(board.board_name, None):
            msg = server.board_manager.hide_board(sess, board.board_name)
    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def refresh_weather(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    server.bot_manager.refresh_weather_info(sess)

    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def add_banner(request):
    '''
    새로운 배너를 등록한다.
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    notice_reg_dic = {}

    # TODO: 아래 필드들 중 하나라도 None 이 들어오면 ... 등록에 들어가지 않아야 한다.
    if request.POST.get('banner_path', None) != None:
        notice_reg_dic['content'] = request.POST['banner_path']
    if request.POST.get('banner_due_date', None) != None:
        year, month, day = tuple(request.POST['banner_due_date'].split('.'))
        notice_reg_dic['due_date'] = datetime2timestamp(datetime.datetime(int(year), int(month), int(day)))
    if request.POST.get('banner_weight', None) != None:
        notice_reg_dic['weight'] = int(request.POST['banner_weight'])

    from arara_thrift.ttypes import WrittenNotice
    server.notice_manager.add_banner(sess, WrittenNotice(**notice_reg_dic))

    return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def select_banner(request):
    '''
    사용자들에게 노출할 배너를 선택한다.
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    banner_list = server.notice_manager.list_banner(sess)
    select_banner_list = request.POST.getlist('select_banner_list')

    for banner in banner_list:
        if unicode(banner.id) in select_banner_list:
            server.notice_manager.modify_banner_validity(sess, banner.id, True)
        else:
            server.notice_manager.modify_banner_validity(sess, banner.id, False)

    return HttpResponseRedirect('/sysop/')
