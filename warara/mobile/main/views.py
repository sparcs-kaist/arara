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

from etc.warara_settings import KSEARCH_ENABLED

@warara.wrap_error_mobile
@warara.prevent_cached_by_browser
def index(request):
    server = warara_middleware.get_server()
    sess, ctx = warara.check_logged_in(request)

    # Redirect to main page if user logged in
    if ctx['logged_in']:
        return HttpResponseRedirect('/mobile/main/')

    if request.session.get('django_language', 0):
        request.session["django_language"] = "en"
    r = server.login_manager.total_visitor()
    r.__dict__['KSEARCH_ENABLED'] = KSEARCH_ENABLED

    rendered = render_to_string('mobile/login.html', r.__dict__)
    return HttpResponse(rendered)

@warara.wrap_error_mobile
@warara.prevent_cached_by_browser
def mobile_main(request):
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

    # Get the today most list
    ret = cache.get('today_most_list')
    if not ret:
        ret = server.article_manager.get_today_most_list(5)
        for item in ret:
            item.date = datetime.datetime.fromtimestamp(item.date)
        cache.set('today_most_list', ret, 60)
    # TODO: Change the key 'todays_best_list' to 'today_best_list'
    #       in both here and Template file.
    ctx['todays_most_list'] = enumerate(ret)

    # Get the weekly-best list
    ret = cache.get('weekly_most_list')
    if not ret:
        ret = server.article_manager.get_weekly_most_list(5)
        for item in ret:
            item.date = datetime.datetime.fromtimestamp(item.date)
        cache.set('weekly_most_list', ret, 60)
    ctx['weekly_most_list'] = enumerate(ret)


    # Get messages for the current user
    if ctx['logged_in']:
        unread_message_count = server.messaging_manager.get_unread_message_count(sess)
        if unread_message_count > 0:
            ctx['new_message'] = True
        else:
            ctx['new_message'] = False

    rendered = render_to_string('mobile/main.html', ctx)
    return HttpResponse(rendered)

