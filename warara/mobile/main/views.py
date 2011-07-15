# coding: utf-8
import sys
import datetime
import warara

from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache

from libs import timestamp2datetime
from warara import warara_middleware

from arara_thrift.ttypes import InvalidOperation
from arara_thrift.ttypes import *



def main(request):
    server = warara_middleware.get_server()
    sess, ctx = warara.check_logged_in(request)

    # Set username if user is guest
    if ctx['username'] == '':
        ctx['username'] = 'Guest'
    # Get the today best list
    ret = cache.get('today_best_list')
    if not ret:
        ret = server.article_manager.get_today_best_list(5)
        for item in ret:
            item.date = datetime.datetime.fromtimestamp(item.date)
        cache.set('today_best_list', ret, 60)
    # TODO: Change the key 'todays_best_list' to 'today_best_list'
    #       in both here and Template file.
    ctx['todays_best_list'] = enumerate(ret)

    # Get the weekly-best list
    ret = cache.get('weekly_best_list')
    if not ret:
        ret = server.article_manager.get_weekly_best_list(5)
        for item in ret:
            item.date = datetime.datetime.fromtimestamp(item.date)
        cache.set('weekly_best_list', ret, 60)
    ctx['weekly_best_list'] = enumerate(ret)

    # Get messages for the current user
    if ctx['logged_in']:
        message_result = server.messaging_manager.receive_list(sess, 1, 1);
        if message_result.new_message_count:
            ctx['new_message'] = True
        else:
            ctx['new_message'] = False

    rendered = render_to_string('main_mobile.html', ctx)
    return HttpResponse(rendered)

