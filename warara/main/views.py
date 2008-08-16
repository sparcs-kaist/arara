# -*- coding: utf-8 -*-
import datetime
import arara
import warara

from django.template.loader import render_to_string
from django.http import HttpResponse

import arara

def index(request):
    if request.session.get('arara_username', '') == 'mikkang':
        del request.session['arara_username'] # XXX : Debugging!
    server = arara.get_server() 
    sess, r = warara.check_logged_in(request)
    
    if sess:
        ret, message = server.member_manager.get_info(sess)
        r['main_nickname'] = message

    SAMPLE_BEST = {
            'todays_best_list': [
                {'title': '아라가 새로 바뀌었다!', 'date': datetime.datetime.now(), 'reply_count': 213},
                {'title': '아라 참 멋지네요', 'date': datetime.datetime.now(), 'reply_count':56},
                {'title': '우왕ㅋ국ㅋ', 'date': datetime.datetime.now(), 'reply_count':44},
                ],
            'weekly_best_list': [
                {'title': '아라가 새로 바뀌었다!', 'date': datetime.datetime.now(), 'reply_count': 213},
                {'title': '아라 참 멋지네요', 'date': datetime.datetime.now(), 'reply_count':56},
                {'title': '우왕ㅋ국ㅋ', 'date': datetime.datetime.now(), 'reply_count':44},
                ],
            }
    SAMPLE_BEST['logged_in'] = r['logged_in']

    max_length = 20 #todays, weekly best max string length
    suc, ret = server.article_manager.get_today_best_list(5)
    for i, tb in enumerate(ret):
        if i==0:
            max_length = 50
        if len(tb['title']) > max_length:
            ret[i]['title'] = ret[i]['title'][0:max_length]
            ret[i]['title'] += '...'
        max_length = 20
    assert suc, ret
    r['todays_best_list'] = enumerate(ret)
    suc, ret = server.article_manager.get_weekly_best_list(5)
    for i, tb in enumerate(ret):
        if i==0:
            continue
        if len(tb['title']) > max_length:
            ret[i]['title'] = ret[i]['title'][0:max_length]
            ret[i]['title'] += '...'
    assert suc, ret
    r['weekly_best_list'] = enumerate(ret)
    
    rendered = render_to_string('index.html', r)
    return HttpResponse(rendered)

def help(request):
    server = arara.get_server() 
    sess, r = warara.check_logged_in(request)
    
    rendered = render_to_string('help.html', r)
    return HttpResponse(rendered)
