#-*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from arara_thrift.ttypes import *
from libs import timestamp2datetime

import warara
from warara import warara_middleware


@warara.wrap_error
def logout(request):
    session_key, r = warara.check_logged_in(request)
    server = warara_middleware.get_server()
    account = server.login_manager.logout(session_key)
    del request.session['arara_session_key']
    del request.session['arara_username']
    del request.session['arara_userid']
    request.session.clear()
    return HttpResponseRedirect('/mobile/login.html')

