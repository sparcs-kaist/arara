from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import arara

def register(request):
    if request.method == 'POST':
        username = request.POST['id']
        password = request.POST['password']
        nickname = request.POST['nickname']
        email = request.POST['email']
        signature = request.POST['sig']
        introduction = request.POST['introduce']
        language = request.POST['language']
        user_information_dic = {'username':username, 'password':password, 'nickname':nickname, 'email':email, 'signature':signature, 'self_introduction':introduction, 'default_language':language}
        server = arara.get_server()
        ret, message = server.member_manager.register(user_information_dic)
        assert ret, message
        return HttpResponseRedirect("/")
    else:
        rendered = render_to_string('account/register.html')
        return HttpResponse(rendered)

def agreement(request):
    rendered = render_to_string('account/register_agreement.html')
    return HttpResponse(rendered)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        client_ip = request.META['REMOTE_ADDR']
        server = arara.get_server()
        ret, session_key = server.login_manager.login(username, password, client_ip)
        assert ret, session_key
        request.session["arara_session_key"] = session_key
        request.session["arara_username"] = username
        return HttpResponseRedirect("/")
    else:
        if "arara_session_key" not in request.session:
            rendered = render_to_string('account/login.html')
            return HttpResponse(rendered)
        else:
            session_key = request.session['arara_session_key']
            server = arara.get_server()
            logged_in = server.login_manager.is_logged_in(session_key)
            if not logged_in:
                del request.session['arara_session_key']
                rendered = render_to_string('account/login.html')
                return HttpResponse(rendered)

            rendered = render_to_string('account/already_logged_in.html')
            return HttpResponse(rendered)


def logout(request):
    session_key = request.session['arara_session_key']
    server = arara.get_server()
    ret, account = server.login_manager.logout(session_key)
    assert ret, message
    return HttpResponseRedirect("/")

def account(request):
    session_key = request.session['arara_session_key']
    server = arara.get_server()
    ret, account = server.member_manager.get_info(session_key)
    assert ret, account

    rendered = render_to_string('account/myaccount_frame.html', account)
    return HttpResponse(rendered)

def account_modify(request):
    session_key = request.session['arara_session_key']
    server = arara.get_server()
    ret, account = server.member_manager.get_info(session_key)
    if request.method == 'POST':
        nickname = request.POST['mynickname']
        signature = request.POST['mysig']
        introduction = request.POST['myintroduce']
        language = request.POST['mylanguage']
        modified_information_dic = {'nickname':nickname, 'signature':signature, 'self_introduction':introduction, 'default_language':language}
        ret, message = server.member_manager.modify(session_key, modified_information_dic)
        assert ret, message
        return HttpResponseRedirect("/account/")
    else:
        rendered = render_to_string('account/myaccount_modify.html', account)
        return HttpResponse(rendered)

def password_modify(request):
    session_key = request.session['arara_session_key']
    server = arara.get_server()
    if request.method == 'POST':
        last_password = request.POST['last_password']
        password = request.POST['password']
        user_information_dic = {'current_password':last_password, 'new_password':password}
        ret, message = server.member_manager.modify(session_key, user_information_dic)
        assert ret, message
        return HttpResponseRedirect("/")
    else:
        rendered = render_to_string('account/myacc_pw_modify.html')
        return HttpResponse(rendered)
