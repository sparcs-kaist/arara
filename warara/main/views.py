# -*- coding: utf-8 -*-
import datetime
import arara
import warara

from django.template.loader import render_to_string
from django.http import HttpResponse

def index(request):
    server = arara.get_server() 
    sess, r = warara.check_logged_in(request)
    suc, ret = server.article_manager.get_today_best_list(5)
    assert suc, ret
    r['todays_best_list'] = ret
    suc, ret = server.article_manager.get_weekly_best_list(5)
    assert suc, ret
    r['weekly_best_list'] = ret
    rendered = render_to_string('index.html', r)
    return HttpResponse(rendered)
