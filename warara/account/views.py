#-*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from arara_thrift.ttypes import *
from libs import timestamp2datetime

import warara
from warara import warara_middleware

@warara.wrap_error
def register(request):
    sess, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    if r['logged_in'] == True:
        raise InvalidOperation("Already logged in!")

    if request.method == 'POST':
        username = request.POST['id']
        password = request.POST['password']
        nickname = request.POST['nickname']
        email = request.POST['email']
        signature = request.POST['sig']
        introduction = request.POST['introduce']
        language = request.POST['language']
        campus = request.POST['campus']
        user_information_dict = {'username':username, 'password':password, 'nickname':nickname, 'email':email, 'signature':signature, 'self_introduction':introduction, 'default_language':language, 'campus':campus}
        message = server.member_manager.register_(UserRegistration(**user_information_dict))
        return HttpResponseRedirect("/main/")
    
    rendered = render_to_string('account/register.html', r)
    return HttpResponse(rendered)



@warara.wrap_error
def confirm_user(request, username, confirm_key):
    server = warara_middleware.get_server()

    try:
        server.member_manager.confirm(username, confirm_key)
        return HttpResponseRedirect("/main/")
    except InvalidOperation:
        return HttpResponse('<script>alert("Confirm failed! \\n\\n  -Wrong confirm key? \\n  -Already confirmed?\\n  -Wrong username?");</script>')
    except InternalError:
        return HttpResponse('<script>alert("Confirm failed! \\n\\nPlease contact ARA SYSOP.");</script>')

@warara.wrap_error
def reconfirm_user(request, username):
    rendered = render_to_string('account/mail_confirm.html',
            {'username': username})
    return HttpResponse(rendered)

@warara.wrap_error
def agreement(request):
    sess, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        raise InvalidOperation("Already logged in!")
    else:
        rendered = render_to_string('account/register_agreement.html')

    return HttpResponse(rendered)

def login_precheck(request):
    # 로그인했다가 그냥 바로 로그아웃하는 함수.
    # username / passwd 점검용으로 사용된다.
    username = request.POST['username']
    password = request.POST['password']
    client_ip = request.META['REMOTE_ADDR']
    server = warara_middleware.get_server()

    try:
        session_key = server.login_manager.login(username, password, client_ip)
        server.login_manager.logout(session_key)
    except InvalidOperation, e:
        return HttpResponse(e.why)

    return HttpResponse("OK")

@warara.wrap_error
def login(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/')

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
    # 임시방편으로, current_page 를 /main 으로 설정해 본다.
    current_page = request.POST.get('current_page_url', '/main')
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
    if User_Info.default_language == "kor":
        request.session["django_language"] = "ko"
    elif User_Info.default_language == "eng":
        request.session["django_language"] = "en"
    request.session["arara_session_key"] = session_key
    request.session["arara_username"] = username
    request.session["arara_userid"] = User_Info.id

    request.session.set_expiry(3600)
    if current_page.find('register')+1:
        return HttpResponseRedirect('/main')
    return HttpResponseRedirect(current_page)

@warara.wrap_error
def logout(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    account = server.login_manager.logout(session_key)
    del request.session['arara_session_key']
    del request.session['arara_username']
    del request.session['arara_userid']
    request.session.clear()
    return HttpResponseRedirect('/')

@warara.wrap_error
def account(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    account = server.member_manager.get_info(session_key)

    account.last_logout_time = timestamp2datetime(account.last_logout_time)
    account.logged_in = True
    rendered = render_to_string('account/myaccount_frame.html', account.__dict__)
    return HttpResponse(rendered)

@warara.wrap_error
def account_modify(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    account = server.member_manager.get_info(session_key)
    if request.method == 'POST':
        nickname = request.POST['mynickname']
        signature = request.POST['mysig']
        introduction = request.POST['myintroduce']
        language = request.POST['mylanguage']
        campus = request.POST['mycampus']
        modified_information_dic = {'nickname': nickname, 'signature': signature, 'self_introduction': introduction, 'default_language': language, 'widget': 0, 'layout': 0, 'campus': campus}
        server.member_manager.modify(session_key, UserModification(**modified_information_dic))
        if language == "kor":
            request.session["django_language"] = "ko"
        elif language == "eng":
            request.session["django_language"] = "en"
        return HttpResponseRedirect("/account/")
    else:
        account.logged_in = True
        rendered = render_to_string('account/myaccount_modify.html', account.__dict__)
        return HttpResponse(rendered)

@warara.wrap_error
def password_modify(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    if request.method == 'POST':
        username = request.session['arara_username']
        last_password = request.POST['last_password']
        password = request.POST['password']
        user_information_dic = {'username':username, 'current_password':last_password, 'new_password':password}
        server.member_manager.modify_password(session_key, UserPasswordInfo(**user_information_dic))
        return HttpResponseRedirect("/account/")
    else:
        if r['logged_in'] == False:
            raise NotLoggedIn("")
        rendered = render_to_string('account/myacc_pw_modify.html', r)
        return HttpResponse(rendered)

@warara.wrap_error
def account_remove(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    if request.method == 'POST':
        server.member_manager.remove_user(session_key)
        return HttpResponseRedirect("/")
    else:
        account = server.member_manager.get_info(session_key)
        account.logged_in = True
        rendered = render_to_string('account/myaccount_remove.html', account.__dict__)
        return HttpResponse(rendered)

def id_check(request):
    if request.method == 'POST':
        server = warara_middleware.get_server()
        r = {}
        check_id_field = request.POST['check_field']
        ret = server.member_manager.is_registered(check_id_field)
        if(request.POST.get('from_message_send', 0)):
            if ret:
                return HttpResponse(1)
            else:
                return HttpResponse(0)
        if ret:
            r = 1
        else:
            r = 0
        return HttpResponse(r)
    else:
        return HttpResponse('Must use POST')

def nickname_check(request):
    if request.method == 'POST':
        server = warara_middleware.get_server()
        r = {}
        check_nickname_field = request.POST['check_field']
        ret = server.member_manager.is_registered_nickname(check_nickname_field)

        if(request.POST.get('from_message_send', 0)): #check from message send or nickname modify
            if ret:
                return HttpResponse(1)
            else:
                return HttpResponse(0)

        if ret:
            r = 1
        else:
            r = 0
        return HttpResponse(r)
    else:
        return HttpResponse('Must use POST')

def email_check(request):
    if request.method == 'POST':
        server = warara_middleware.get_server()
        r = {}
        check_email_field = request.POST['check_email_field']
        ret = server.member_manager.is_registered_email(check_email_field)
        if ret:
            r = 1
        else:
            r = 0
        return HttpResponse(r)
    else:
        return HttpResponse('Must use POST')

@warara.wrap_error
def mail_resend(request):
    # XXX : Combacsa modified this code... might not work well...
    # XXX : pipoket also modified this code :)
    sess, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    if r['logged_in'] == True:
        raise InvalidOperation("Already logged in!")

    if request.method == 'POST':
        username  = request.POST['id']
        new_email = request.POST['email']
        message = server.member_manager.modify_authentication_email(username, new_email)
        return HttpResponseRedirect("/main/")
