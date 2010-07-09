#-*- coding: utf-8 -*-
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

    # _weather 보드가 있는지 확인하고, 없으면 새로 생성한다.
    # 제안하는 convention : 보드 이름이 _ 로 시작하면 무조건 hide 속성을 부여하는 건 어떨까.
    board_list = server.board_manager.get_board_list()
    if not filter(lambda x:x.board_name == '_weather', board_list):
        server.board_manager.add_board(sess, '_weather', u'Board for weather (should be hidden)', []) # 말머리는 없다
        server.board_manager.hide_board(sess, '_weather')

    # 날씨 정보를 받아온다.
    # 날씨 정보 출처 : 기상청 (www.kma.go.kr)
    import urllib
    import time
    today_string = time.strftime("%Y-%m-%d (%a) %H:%M:%s", time.localtime())
    xmlsession = urllib.urlopen('http://www.kma.go.kr/wid/queryDFSRSS.jsp?zone=3020055000')
    weather_xml = xmlsession.read()
    xmlsession.close()

    # 받아온 날씨 정보를 새로운 글로 작성한다.
    from arara_thrift.ttypes import WrittenArticle
    article_dic = {'title': today_string, 'content': weather_xml}
    server.article_manager.write_article(sess, '_weather', WrittenArticle(**article_dic))

    return HttpResponseRedirect('/sysop/')
