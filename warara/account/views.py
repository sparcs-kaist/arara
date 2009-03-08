from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from arara_thrift.ttypes import *
from arara.util import timestamp2datetime

import arara
import warara

@warara.wrap_error
def register(request):
    sess, r = warara.check_logged_in(request)
    server = arara.get_server()
    if r['logged_in'] == True:
        assert None, "ALEADY_LOGGED_IN"

    if request.method == 'POST':
        username = request.POST['id']
        password = request.POST['password']
        nickname = request.POST['nickname']
        email = request.POST['email']
        signature = request.POST['sig']
        introduction = request.POST['introduce']
        language = request.POST['language']
        user_information_dict = {'username':username, 'password':password, 'nickname':nickname, 'email':email, 'signature':signature, 'self_introduction':introduction, 'default_language':language}
        message = server.member_manager.register(UserRegistration(**user_information_dict))
        return HttpResponseRedirect("/main/")
    
    rendered = render_to_string('account/register.html', r)
    return HttpResponse(rendered)



@warara.wrap_error
def confirm_user(request, username, confirm_key):
    server = arara.get_server()

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
        assert None, "ALREADY_LOGGED_IN"
    else:
        rendered = render_to_string('account/register_agreement.html')

    return HttpResponse(rendered)

@warara.wrap_error
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        current_page = request.POST.get('current_page_url', 0)
        client_ip = request.META['REMOTE_ADDR']
        server = arara.get_server()

        try:
            session_key = server.login_manager.login(username, password, client_ip)
        except InvalidOperation, e:
            if request.POST.get('precheck', 0):
                return HttpResponse(e)
            else:
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

        if request.POST.get('precheck', 0):
            return HttpResponse("OK")

        User_Info = server.member_manager.get_info(session_key)
        if User_Info.default_language == "kor":
            request.session["django_language"] = "ko"
        elif User_Info.default_language == "eng":
            request.session["django_language"] = "en"
        request.session["arara_session_key"] = session_key
        request.session["arara_username"] = username

        request.session.set_expiry(3600)
        if current_page.find('register')+1:
            return HttpResponseRedirect('/main')
        return HttpResponseRedirect(current_page)

    return HttpResponseRedirect('/')

@warara.wrap_error
def logout(request):
    session_key, r = warara.check_logged_in(request)
    server = arara.get_server()
    account = server.login_manager.logout(session_key)
    del request.session['arara_session_key']
    del request.session['arara_username']
    request.session.clear()
    return HttpResponseRedirect('/')

@warara.wrap_error
def account(request):
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        account = server.member_manager.get_info(session_key)

        account.last_logout_time = timestamp2datetime(account.last_logout_time)
        account.logged_in = True
        rendered = render_to_string('account/myaccount_frame.html', account.__dict__)
    else:
        assert None, "NOT_LOGGED_IN"
    return HttpResponse(rendered)

@warara.wrap_error
def account_modify(request):
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        account = server.member_manager.get_info(session_key)
        if request.method == 'POST':
            nickname = request.POST['mynickname']
            signature = request.POST['mysig']
            introduction = request.POST['myintroduce']
            language = request.POST['mylanguage']
            modified_information_dic = {'nickname': nickname, 'signature': signature, 'self_introduction': introduction, 'default_language': language, 'widget': 0, 'layout': 0}
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
    else:
        assert None, "NOT_LOGGED_IN"
        return HttpResponse(rendered)

@warara.wrap_error
def password_modify(request):
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        if request.method == 'POST':
            username = request.session['arara_username']
            last_password = request.POST['last_password']
            password = request.POST['password']
            user_information_dic = {'username':username, 'current_password':last_password, 'new_password':password}
            server.member_manager.modify_password(session_key, UserPasswordInfo(**user_information_dic))
            return HttpResponseRedirect("/account/")
        else:
            rendered = render_to_string('account/myacc_pw_modify.html', r)
            return HttpResponse(rendered)

    else:
        assert None, "NOT_LOGGED_IN"

@warara.wrap_error
def account_remove(request):
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        if request.method == 'POST':
            server.member_manager.remove_user(session_key)
            return HttpResponseRedirect("/")
        else:
            account = server.member_manager.get_info(session_key)
            account.logged_in = True
            rendered = render_to_string('account/myaccount_remove.html', account.__dict__)
            return HttpResponse(rendered)
    else:
        assert None, "NOT_LOGGED_IN"
        return HttpResponse(rendered)


def id_check(request):
    if request.method == 'POST':
        server = arara.get_server()
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
        server = arara.get_server()
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
        server = arara.get_server()
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

def mail_resend(request):
    # XXX : Combacsa modified this code... might not work well...
    sess, r = warara.check_logged_in(request)
    server = arara.get_server()
    if r['logged_in'] == True:
        assert None, "ALEADY_LOGGED_IN"

    if request.method == 'POST':
        username  = request.POST['id']
        new_email = request.POST['email']
        message = server.member_manager.modify_authentication_email(username, new_email)
        return HttpResponseRedirect("/main/")

    assert None, "INTERNAL_SERVER_ERROR"
