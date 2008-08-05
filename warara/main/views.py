# -*- coding: utf-8 -*-
import datetime
import arara
import warara

from django.template.loader import render_to_string
from django.http import HttpResponse

import arara

def index(request):
    server = arara.get_server() 
    sess, r = warara.check_logged_in(request)

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

    suc, ret = server.article_manager.get_today_best_list(5)
    assert suc, ret
    r['todays_best_list'] = ret
    suc, ret = server.article_manager.get_weekly_best_list(5)
    assert suc, ret
    r['weekly_best_list'] = ret

    if 'search' in request.GET:
        query = request.GET['search']
        search_type = 'username'
        if 'search_type_main' in request.GET:
            search_type = request.GET['search_type_main']
        search_user_info = {search_type: query}
        ret, user_id = server.member_manager.search_user(sess, search_user_info)
        if ret:
            r['search_result'] = user_id
    
    rendered = render_to_string('index.html', r)
    return HttpResponse(rendered)
