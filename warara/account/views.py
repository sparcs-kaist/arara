#-*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from arara_thrift.ttypes import *
from libs import timestamp2datetime

import warara
from warara import warara_middleware

import hashlib

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

def confirm_passive(request):
    # TODO: POST 로 넘어오지 않았을 때는 어떻게 대처해야 하는가?
    if request.method == 'POST':
        username = request.POST['id']
        nickname = request.POST['nickname']
        confirm_key = request.POST['confirm_key'];
        server = warara_middleware.get_server()
        try:
            server.member_manager.confirm(username, confirm_key)
            return HttpResponseRedirect("/main/")
        except InvalidOperation:
            return HttpResponse('<script>alert("Confirm failed! \\n\\n  -Wrong confirm key? \\n  -Alreday confirmed?\\n  -Wrong username?);</script>')
        except InternalError:
            return HttpResponse('<script>alert("Confirm failed! \\n\\nPlease contact ARA SYSOP.");</script>')

def confirm_passive_url(request):
    # TODO: POST 로 넘어오지 않았을 때는 어떻게 대처해야 하는가?
    if request.method == 'POST':
        username = request.POST['id']
        nickname = request.POST['nickname']
        rendered = render_to_string('account/mail_confirm_passive.html',{'username':username,'nickname':nickname})
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
def cancel_confirm(request, username):
    server = warara_middleware.get_server()

    try:
        server.member_manager.cancel_confirm(username)
    except InvalidOperation:
        return HttpResponse('<script>alert("Failed! \\n\\n  -Already canceled?\\n  -Not confirmed? \\n  -Wrong username?");</script>')
    except InternalError:
        return HttpResponse('<script>alert("Failed! \\n\\nPlease contact ARA SYSOP.");</script>')

    return logout(request)

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

    # 로그인 요청을 수행한 url 을 current_page 로 설정한다
    # 해당되는 url 이 없을 경우 /main/ 을 기본값으로 설정한다
    current_page = request.POST.get('current_page_url', '/main/')

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
        response = HttpResponseRedirect('/main/')
    else:
        response = HttpResponseRedirect(current_page)

    # Additional cookie for detect session mismatch
    checksum = hashlib.sha1(session_key+"@"+username).hexdigest()
    response.set_cookie(key='arara_checksum', value=checksum, max_age=None)

    import logging
    logger = logging.getLogger('main')
    logger.info('WARARA Login: name %s, key %s, django sessid %s' % (username, session_key, request.session.session_key))
    return response

@warara.wrap_error
def logout(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    account = server.login_manager.logout(session_key)
    del request.session['arara_session_key']
    del request.session['arara_username']
    del request.session['arara_userid']
    request.session.clear()

    response = HttpResponseRedirect('/')
    response.delete_cookie('arara_checksum')
    return response

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
        listing_mode = int(request.POST['mylistingmode'])
        modified_information_dic = {'nickname': nickname, 'signature': signature, 'self_introduction': introduction, 'default_language': language, 'widget': 0, 'layout': 0, 'campus': campus, 'listing_mode': listing_mode}
        server.member_manager.modify_user(session_key, UserModification(**modified_information_dic))
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
        del request.session['arara_session_key']
        del request.session['arara_username']
        del request.session['arara_userid']
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

def id_recovery(request):
    if request.method == 'POST':
        server = warara_middleware.get_server()
        email = request.POST.get('email_field', '')

        if email == '':
            error_msg = 'Fill the e-mail field!'
        elif server.member_manager.send_id_recovery_email(email):
            error_msg = 'We sent a mail. Check your mailbox.'
        else:
            error_msg = 'That user doesn`t exist.'
        return HttpResponse('<script>alert("%s"); history.back(); </script>' % error_msg)
    else:
        rendered = render_to_string('account/id_recovery.html')
        return HttpResponse(rendered)

def send_password_recovery_email(request):
    sess, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    if r['logged_in'] == True:
        raise InvalidOperation("Already logged in!")

    if request.method == 'POST':
        username = request.POST.get('username_field', '')
        email = request.POST.get('email_field', '')

        error_msg = ''
        if not username:
            error_msg = 'Username field is empty.'
        if not email:
            error_msg = 'Email field is empty.'
        if error_msg:
            return HttpResponse('<script>alert("%s"); history.back(); </script>' % error_msg)

        try:
            server.member_manager.send_password_recovery_email(username, email)
            resp = "We sent e-mail to your e-mail address. Please check your inbox."
        except InvalidOperation, e:
            resp = e.why

        return HttpResponse('<script>alert("%s"); history.back(); </script>' % resp)
    else:
        rendered = render_to_string('account/password_recovery_send_email.html', r)
        return HttpResponse(rendered)

def password_recovery(request, username, token_code):
    sess, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    if r['logged_in'] == True:
        raise InvalidOperation("Already logged in!")

    if request.method == 'POST':
        new_password = request.POST.get('password', '')
        new_password_check = request.POST.get('re_password', '')

        error_msg = ''
        if new_password != new_password_check:
            error_msg = 'Passwords are not agree.'
        if new_password == '':
            error_msg = 'Password cannot be empty.'
        if error_msg:
            return HttpResponse('<script>alert("%s"); history.back(); </script>' % error_msg)

        user_password_dic = {'username':username, 'current_password':u'', 'new_password':new_password}
        try:
            server.member_manager.modify_password_with_token(UserPasswordInfo(**user_password_dic), token_code)
        except InvalidOperation, e:
            return HttpResponse('<script>alert("%s"); history.back(); </script>' % e.why)

        return HttpResponseRedirect("/")
    else:
        r['username'] = username
        r['token_code'] = token_code
        rendered = render_to_string('account/password_recovery_process.html', r)
        return HttpResponse(rendered)


@warara.wrap_error
def mark_all_articles(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    account = server.read_status_manager.mark_all_articles(session_key)
    return HttpResponseRedirect('/account/')

@warara.wrap_error
def unmark_all_articles(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    account = server.read_status_manager.unmark_all_articles(session_key)
    return HttpResponseRedirect('/account/')
