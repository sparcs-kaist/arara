#-*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from arara_thrift.ttypes import *
from libs import timestamp2datetime

import warara
from warara import warara_middleware
import hashlib

@warara.prevent_cached_by_browser
@warara.wrap_error_mobile
def login(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/mobile/')

    if request.POST.get('precheck', 0):
        return login_precheck(request)

    # 가끔 username / password 를 아예 안 넣는 경우가 있다.
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    if username == None or password == None:
        # XXX 2010.07.02. 사실 합당한 에러를 만들어야 하는데 ...
        raise NotLoggedIn()

    # XXX 2010.05.15.
    # 경위는 알 수 없지만 current_page_url 이 넘어오지 않아서
    # current_page 값이 진짜로 0 이 되어버리는 사례가 있었다.
    # 따라서 저~~ 아래에서 current_page.find 를 호출하면
    # int 에 대해서 호출하므로 맛이 가버리는 일이 발생한다.
    # 임시방편으로, current_page 를 /mobile/main 으로 설정해 본다. ( 모바일! )
    current_page = request.POST.get('current_page_url', '/mobile/main')
    # XXX 여기까지.
    client_ip = request.META['REMOTE_ADDR']
    server = warara_middleware.get_server()

    try:
        session_key = server.login_manager.login(username, password, client_ip)
    except InvalidOperation, e:
        #XXX: (pipoket) Ugly hack for showing nickname while not logged in.
        # print e.why
        splited = e.why.splitlines()
        if splited[0] == 'not activated':
            username = splited[1]
            nickname = splited[2]
            rendered = render_to_string('account/mail_confirm.html', {
                'username': username, 'nickname': nickname})
            return HttpResponse(rendered)
        else:
            return HttpResponse('<script>alert("Login failed!"); history.back()</script>');

    User_Info = server.member_manager.get_info(session_key)
    # Check mismatch
    if User_Info.username.lower() != username.lower():
        server.login_manager.debug__check_session(session_key, username, client_ip, User_Info)
        server.login_manager.logout(session_key)
        return HttpResponse('<script>alert("Something is Wrong. Please report to Sysop."); history.back()</script>')

    if User_Info.default_language == "kor":
        request.session["django_language"] = "ko"
    elif User_Info.default_language == "eng":
        request.session["django_language"] = "en"
    request.session["arara_session_key"] = session_key
    request.session["arara_username"] = username
    request.session["arara_userid"] = User_Info.id

    # request.session.set_expiry(3600)   NO use with SESSION_EXPIRE_AT_BROWSER_CLOSE
    if current_page.find('register')+1:
        response = HttpResponseRedirect('/mobile/main/')
    else:
        response = HttpResponseRedirect(current_page)

    # Additional cookie for detect session mismatch
    checksum = hashlib.sha1(session_key+"@"+username).hexdigest()
    response.set_cookie(key='arara_checksum', value=checksum, max_age=None)
    return response

@warara.prevent_cached_by_browser
@warara.wrap_error_mobile
def logout(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    account = server.login_manager.logout(session_key)
    del request.session['arara_session_key']
    del request.session['arara_username']
    del request.session['arara_userid']
    request.session.clear()

    response = HttpResponseRedirect('/mobile/')
    response.delete_cookie('arara_checksum')
    return response

