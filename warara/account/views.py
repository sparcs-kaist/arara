from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from email.MIMEText import MIMEText

import smtplib
import arara
import warara

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
        user_information_dic = {'username':username, 'password':password, 'nickname':nickname, 'email':email, 'signature':signature, 'self_introduction':introduction, 'default_language':language}
        ret, message = server.member_manager.register(user_information_dic)
        assert ret, message
        send_mail(email, username, message)
        return HttpResponseRedirect("/")
    
    rendered = render_to_string('account/register.html', r)
    return HttpResponse(rendered)

'''
def send_mail(email, username, confirm_key):
    sender = 'root_id@sparcs.org' #pv457, no_reply, ara, ara_admin
    receiver = email
    content = render_to_string('account/send_mail.html', {'username':username, 'confirm_key':confirm_key})
    subject = "confirm" + username
    msg = EmailMultiAlternatives(subject, '', sender, [receiver])
    msg.attach_alternative(content, "text/html")
    msg.send()
'''

def send_mail(email, username, confirm_key):
    HOST = 'smtp.naver.com'
    sender = 'root_id@sparcs.org'
    content = render_to_string('account/send_mail.html', {'username':username, 'confirm_key':confirm_key})
    title = "confirm"
    msg = MIMEText(content, _subtype="html", _charset='euc_kr')
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = email
    s = smtplib.SMTP()
    s.connect(HOST)
    s.login('newtron_star', 'q1q1q1')
    s.sendmail(sender, [email], msg.as_string())
    s.quit()

def confirm_user(request, username, confirm_key):
    server = arara.get_server()

    if request.method == 'POST':
        ret, mes = server.member_manager.confirm(username, confirm_key)
        return HttpResponse(mes)

    rendered = render_to_string('account/mail_confirm.html')
    return HttpResponse(rendered)

def agreement(request):
    sess, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        assert None, "ALREADY_LOGGED_IN"
    else:
        rendered = render_to_string('account/register_agreement.html')

    return HttpResponse(rendered)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        current_page = request.POST['current_page_url']
        client_ip = request.META['REMOTE_ADDR']
        server = arara.get_server()
        ret, session_key = server.login_manager.login(username, password, client_ip)
        assert ret, session_key
        request.session["arara_session_key"] = session_key
        request.session["arara_username"] = username
        return HttpResponseRedirect(current_page)

    return HttpResponseRedirect('/')

def logout(request):
    if request.session.get('arara_session_key', 0):
        del request.session['arara_session_key']
        del request.session['arara_username']
        return HttpResponseRedirect("/")
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        ret, account = server.login_manager.logout(session_key)
        del request.session['arara_session_key']
        del request.session['arara_username']
        request.session.clear()
        assert ret, account
        return HttpResponseRedirect(current_page)
    else:
        if request.session.get('arara_session_key', 0):
            del request.session['arara_session_key']
            del request.session['arara_username']
        assert None, "NOT_LOGGED_IN"

def account(request):
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        ret, account = server.member_manager.get_info(session_key)
        assert ret, account

        account['logged_in'] = True
        rendered = render_to_string('account/myaccount_frame.html', account)
    else:
        assert None, "NOT_LOGGED_IN"
    return HttpResponse(rendered)

def account_modify(request):
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        ret, account = server.member_manager.get_info(session_key)
        if request.method == 'POST':
            nickname = request.POST['mynickname']
            signature = request.POST['mysig']
            introduction = request.POST['myintroduce']
            language = request.POST['mylanguage']
            modified_information_dic = {'nickname': nickname, 'signature': signature, 'self_introduction': introduction, 'default_language': language, 'widget': 0, 'layout': 0}
            ret, message = server.member_manager.modify(session_key, modified_information_dic)
            assert ret, message
            return HttpResponseRedirect("/account/")
        else:
            account['logged_in'] = True
            rendered = render_to_string('account/myaccount_modify.html', account)
            return HttpResponse(rendered)
    else:
        assert None, "NOT_LOGGED_IN"
        return HttpResponse(rendered)

def password_modify(request):
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        if request.method == 'POST':
            username = request.session['arara_username']
            last_password = request.POST['last_password']
            password = request.POST['password']
            user_information_dic = {'username':username, 'current_password':last_password, 'new_password':password}
            ret, message = server.member_manager.modify_password(session_key, user_information_dic)
            assert ret, message
            return HttpResponseRedirect("/account/")
        else:
            rendered = render_to_string('account/myacc_pw_modify.html')
            return HttpResponse(rendered)

    else:
        assert None, "NOT_LOGGED_IN"

def account_remove(request):
    session_key, r = warara.check_logged_in(request)
    if r['logged_in'] == True:
        server = arara.get_server()
        if request.method == 'POST':
            ret, message = server.member_manager.remove_user(session_key)
            assert ret, message
            return HttpResponseRedirect("/")
        else:
            account = {}
            account['logged_in'] = True
            rendered = render_to_string('account/myaccount_remove.html', account)
            return HttpResponse(rendered)
    else:
        assert None, "NOT_LOGGED_IN"
        return HttpResponse(rendered)

def wrap_error(f):
    def check_error(*args, **argv):
        r = {} #render item
        try:
            return f(*args, **argv)
        except AssertionError, e:
            if e.message == "NOT_LOGGED_IN":
                r['error_message'] = "not logged in!"
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)
            elif e.message == "ALEADY_LOGGED_IN":
                r['error_message'] = "aleady logged in"
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)

            r['error_message'] = "unknown keyerror : " + e.message
            rendered = render_to_string("error.html", r)
            return HttpResponse(rendered)
                
        except KeyError, e:
            if e.message == "arara_session_key":
                r['error_message'] = "not logged in!"
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)
            
            r['error_message'] = "unknown keyerror : " + e.message
            rendered = render_to_string("error.html", r)
            return HttpResponse(rendered)

    return check_error

#login = wrap_error(login)
#logout = wrap_error(logout)
account = wrap_error(account)
register = wrap_error(register)
agreement = wrap_error(agreement)
confirm_user = wrap_error(confirm_user)
account_modify = wrap_error(account_modify)
account_remove = wrap_error(account_remove)
password_modify = wrap_error(password_modify)

def id_check(request):
    if request.method == 'POST':
        server = arara.get_server()
        r = {}
        check_id_field = request.POST['check_id_field']
        ret = server.member_manager.is_registered(check_id_field)
        if ret:
            r = 'The ID is not available'
        else:
            r = 'The ID is available'
        return HttpResponse(r)
    else:
        return HttpResponse('Must use POST')

def nickname_check(request):
    if request.method == 'POST':
        server = arara.get_server()
        r = {}
        check_nickname_field = request.POST['check_nickname_field']
        ret = server.member_manager.is_registered_nickname(check_nickname_field)
        if ret:
            r = 'The nickname is not available'
        else:
            r = 'The nickname is available'
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
            r = 'The email is not available'
        else:
            r = 'The email is available'
        return HttpResponse(r)
    else:
        return HttpResponse('Must use POST')
