#-*- coding: utf-8 -*-
import datetime
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import warara
from warara import warara_middleware

from libs import datetime2timestamp

@warara.wrap_error
def index(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    board_list = server.board_manager.get_board_list()
    r['board_list'] = board_list
    
    bbs_managers_list = []
    for board in board_list:
        bbs_managers = server.board_manager.get_bbs_managers(board.board_name)
        bbs_managers_list.append({'board': board, 'managers': bbs_managers})
    r['bbs_managers_list'] = bbs_managers_list

    r['category_list'] = server.board_manager.get_category_list() + [{'category_name':'None'}]

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

    category_name = request.POST.get('add_board_category', None)
    if category_name == "None": category_name = None
    server.board_manager.add_board(sess, request.POST['add_board_name'], request.POST['add_board_description'], board_headings, category_name, int(request.POST['add_board_type']), int(request.POST['to_read_level']), int(request.POST['to_write_level']))
    return HttpResponseRedirect('/sysop/')

def _ajax_calling(response):
    '''
    ajax 사용 시 보낼 갱신된 보드 정보(html 태그 포함)를 완성해 돌려준다.
    '''
    server = warara_middleware.get_server()
    board_list = server.board_manager.get_board_list()
    for board in board_list:
        bbs_managers = server.board_manager.get_bbs_managers(board.board_name)
        managers_string = "".join(("*"+manager.username+" " for manager in bbs_managers))
        response += "\n" + board.board_name + "\t" + board.board_description + "\t" + ("hidden_board" if board.hide else "showing_board") + "\t" + str(board.to_read_level) + "\t" + str(board.to_write_level) + "\t" + managers_string
    return response


@warara.wrap_error
def modify_board(request):
    '''
    선택된 보드를 삭제 / 숨김 / 숨김 해제한다.
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    board_list = server.board_manager.get_board_list()
    # 어떤 보드에 대한 명령인지 확인하고 해당 보드의 객체를 얻는다. 
    requested_board_name = request.POST.get(u'board_name', None)
    if requested_board_name == None:
        msg = "board not specified"
        HttpResponseRedirect('/sysop/')
    requested_board = None
    for board in board_list:
        if requested_board_name == board.board_name:
            requested_board = board
            break
    if requested_board == None:
        msg = "unknown board"
        HttpResponseRedirect('/sysop/')
    # 어떤 명령을 주었는지 확인하고 처리한다.
    action = request.POST.get('action', None)
    if action == None:
        msg = "action not specified"
        return HttpResponseRedirect('/sysop/')
    if action == 'remove':
        msg = server.board_manager.delete_board(sess, requested_board.board_name)
    elif action == 'hide':
        msg = server.board_manager.hide_board(sess, requested_board.board_name)
    elif action == 'return_hide':
        msg = server.board_manager.return_hide_board(sess, requested_board.board_name)
    elif action == 'moveup':
        if requested_board.order > 1:
            msg = server.board_manager.change_board_order(sess, requested_board.board_name, requested_board.order - 1)
    elif action == 'movedown':
        if requested_board.order < len(filter(lambda b:b.order != None, board_list)):
            msg = server.board_manager.change_board_order(sess, requested_board.board_name, requested_board.order + 1)
    else:
        msg = "unknown_sysop_board_modification_command"
        return HttpResponseRedirect('/sysop/')
    # AJAX로 온 요청일 때에는 갱신된 보드 정보를 보낸다. 
    if request.is_ajax():
        response = "SUCCESS\t" + action + "\t" + requested_board_name
        response = _ajax_calling(response)
        return HttpResponse(response)
    else:
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

    if request.is_ajax():
        response = "SUCCESS\tedit\t" + new_board_name
        response = _ajax_calling(response)
        return HttpResponse(response)
    else:
        return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def change_auth(request):
    '''
    선택된 보드정보와 읽기/쓰기 권한 정보를 받아서 게시판의 권한 설정을 바꾼다.
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    server.board_manager.change_auth(sess, request.POST['orig_board_name'], int(request.POST['change_read_level']), int(request.POST['change_write_level']))

    if request.is_ajax():
        response = "SUCCESS\tchange_auth\t" + request.POST['orig_board_name']
        response = _ajax_calling(response)
        return HttpResponse(response)
    else:
        return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def add_bbs_manager(request):
    '''
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    board_name = request.POST['board_name']
    manager = request.POST['manager']
    server.board_manager.add_bbs_manager(sess, board_name, manager)

    if request.is_ajax():
        response = "SUCCESS\tadd_manager\t" + board_name
        response = _ajax_calling(response)
        return HttpResponse(response)
    else:
        return HttpResponseRedirect('/sysop/')

@warara.wrap_error
def remove_bbs_manager(request):
    '''
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    board_name = request.POST['board_name']
    manager = request.POST['manager']
    server.board_manager.remove_bbs_manager(sess, board_name, manager)
    if request.is_ajax():
        response = "SUCCESS\tremove_manager\t" + board_name
        response = _ajax_calling(response)
        return HttpResponse(response)
    else:
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
def add_category(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    new_category_name = request.POST.get('add_board_name', None)
    if not new_category_name:
        return HttpResponseRedirect('/sysop')

    try:
        server.board_manager.add_category(sess, new_category_name)
    except:
        raise
    return HttpResponseRedirect('/sysop')

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
