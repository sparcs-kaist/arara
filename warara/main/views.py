# -*- coding: utf-8 -*-
import sys
import datetime
import arara
import warara

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.cache import cache

import arara

def index(request):
    r = {}
    r['counter_today'] = 1048576
    r['counter_total'] = 2147483647
    rendered = render_to_string('index.html', r)
    return HttpResponse(rendered)

@warara.cache_page(60)
def main(request):
    server = arara.get_server() 
    sess, r = warara.check_logged_in(request)

    max_length = 20 #todays, weekly best max string length
    ret = cache.get('today_best_list')
    if not ret:
        suc, ret = server.article_manager.get_today_best_list(5)
        cache.set('todays_best_list', ret, 60)
    if not suc: #XXX
        rendered = render_to_string('main.html', r)
        return HttpResponse(rendered)
    for i, tb in enumerate(ret):
        if i==0:
            max_length = 50
        if len(tb['title']) > max_length:
            ret[i]['title'] = ret[i]['title'][0:max_length]
            ret[i]['title'] += '...'
        max_length = 20
    assert suc, ret
    r['todays_best_list'] = enumerate(ret)
    ret = cache.get('weekly_best_list')
    if not ret:
        suc, ret = server.article_manager.get_weekly_best_list(5)
        cache.set('weekly_best_list', ret, 60)
    for i, tb in enumerate(ret):
        if i==0:
            continue
        if len(tb['title']) > max_length:
            ret[i]['title'] = ret[i]['title'][0:max_length]
            ret[i]['title'] += '...'
    assert suc, ret
    r['weekly_best_list'] = enumerate(ret)

    if request.method == 'POST':
        session_key, r = warara.check_logged_in(request)
        server = arara.get_server()
        query_user_name = request.POST['query_user_name']
        ret, information = server.member_manager.query_by_username(session_key, query_user_name)
        assert ret, information
        rendered = render_to_string('account/another_user_account.html', information)
        return HttpResponse(rendered)

    else:
        rendered = render_to_string('main.html', r)
        return HttpResponse(rendered)

def help(request):
    server = arara.get_server() 
    sess, r = warara.check_logged_in(request)
    
    rendered = render_to_string('help.html', r)
    return HttpResponse(rendered)


def wrap_error(f):
    def check_error(*args, **argv):
        r = {} #render item
        try:
            return f(*args, **argv)
        except StandardError, e:
            if e.message == "NOT_LOGGED_IN":
                r['error_message'] = e.message
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)
            elif e.message == "arara_session_key":
                r['error_message'] = "NOT_LOGGED_IN"
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)
            else:
                rendered = render_to_string("error.html")
                return HttpResponse(rendered)

    return check_error

index = wrap_error(index)
help = wrap_error(help)
main = wrap_error(main)
