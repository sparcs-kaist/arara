# -*- coding: utf-8 -*-
import sys
import datetime
import arara
import warara

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.cache import cache

import arara
from arara.util import timestamp2datetime

@warara.wrap_error
def index(request):
    server = arara.get_server()
    if request.session.get('django_language', 0):
        request.session["django_language"] = "en"
    r = server.login_manager.total_visitor()
    rendered = render_to_string('index.html', r.__dict__)
    return HttpResponse(rendered)

@warara.wrap_error
@warara.cache_page(60)
def main(request):
    server = arara.get_server() 
    sess, r = warara.check_logged_in(request)

    max_length = 45 #todays, weekly best max string length
    ret = cache.get('today_best_list')
    if not ret:
        ret = server.article_manager.get_today_best_list(5)
        for item in ret:
            item.date = datetime.datetime.fromtimestamp(item.date)
        cache.set('todays_best_list', ret, 60)
    r['todays_best_list'] = enumerate(ret)
    ret = cache.get('weekly_best_list')
    if not ret:
        ret = server.article_manager.get_weekly_best_list(5)
        for item in ret:
            item.date = datetime.datetime.fromtimestamp(item.date)
        cache.set('weekly_best_list', ret, 60)
    r['weekly_best_list'] = enumerate(ret)

    #message_check
    if r['logged_in']:
        message_result = server.messaging_manager.receive_list(sess, 1, 1);

        if message_result.new_message_count:
            r['new_message'] = True
        else:
            r['new_message'] = False

    r['banner_tag'] = '<img src="/media/image/banner_1.png" alt="banner">'
    rendered = render_to_string('main.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def help(request):
    server = arara.get_server() 
    sess, r = warara.check_logged_in(request)
    
    rendered = render_to_string('help.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def get_user_info(request):
    if request.method == 'POST':
        session_key, r = warara.check_logged_in(request)
        server = arara.get_server()
        query_user_name = request.POST['query_user_name']
        information = server.member_manager.query_by_username(session_key, query_user_name)
        information.last_logout_time = timestamp2datetime(information.last_logout_time)
        rendered = render_to_string('account/another_user_account.html', information.__dict__)
        return HttpResponse(rendered)
    else:
        return HttpResponse("Linear Algebra")
    assert ret, information
