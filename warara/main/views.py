# -*- coding: utf-8 -*-
import sys
import datetime
import warara

from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache

from libs import timestamp2datetime
from warara import warara_middleware

from arara_thrift.ttypes import InvalidOperation
from etc.warara_settings import USE_WEATHER_FORECAST, WEATHER_ICON_PATH, WEATHER_ICON_SET
from arara_thrift.ttypes import *

@warara.wrap_error
def index(request):
    server = warara_middleware.get_server()
    sess, ctx = warara.check_logged_in(request)

    # Redirect to main page if user logged in
    if ctx['logged_in']:
        return HttpResponseRedirect('/main/')

    if request.session.get('django_language', 0):
        request.session["django_language"] = "en"
    r = server.login_manager.total_visitor()
    rendered = render_to_string('index.html', r.__dict__)
    return HttpResponse(rendered)

@warara.wrap_error
@warara.cache_page(60)
def main(request):
    server = warara_middleware.get_server() 
    sess, ctx = warara.check_logged_in(request)
    # TODO: rename all 'r' variables to 'ctx' that means 'context'.

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

    # Get banner
    try:
        ctx['banner'] = server.notice_manager.get_banner()
        ctx['has_banner'] = True
    except InvalidOperation:
        ctx['has_banner'] = False

    # Get Weather info
    if USE_WEATHER_FORECAST:
        ctx['weather_info'] = server.bot_manager.get_weather_info(sess)
        if ctx['weather_info'].city == None:
            ctx['has_weather'] = False
        else:
            if ctx['weather_info'].city.lower() == 'daejeon':
                ctx['weather_info'].city = u'대전'
            elif ctx['weather_info'].city.lower == 'seoul':
                ctx['weather_info'].city = u'서울'

            ctx['weather_info'].current_icon_url = weather_icon_replace(ctx['weather_info'].current_icon_url)
            ctx['weather_info'].tomorrow_icon_url = weather_icon_replace(ctx['weather_info'].tomorrow_icon_url)
            ctx['weather_info'].day_after_tomorrow_icon_url = weather_icon_replace(ctx['weather_info'].day_after_tomorrow_icon_url)
            ctx['has_weather'] = True
    else:
        ctx['has_weather'] = False
    
    rendered = render_to_string('main.html', ctx)
    return HttpResponse(rendered)

@warara.wrap_error
def help(request):
    server = warara_middleware.get_server() 
    sess, ctx = warara.check_logged_in(request)
    
    rendered = render_to_string('help.html', ctx)
    return HttpResponse(rendered)

@warara.wrap_error
def get_user_info(request):
    if request.method == 'POST':
        session_key, ctx = warara.check_logged_in(request)
        server = warara_middleware.get_server()
        query_user_name = request.POST['query_user_name']
        information = server.member_manager.query_by_username(session_key, query_user_name)
        information.last_logout_time = timestamp2datetime(information.last_logout_time)
        rendered = render_to_string('account/another_user_account.html', information.__dict__)
        return HttpResponse(rendered)
    else:
        return HttpResponse("Linear Algebra")
    assert ret, information

def weather_icon_replace(orig_url):
    # google의 icon을 아라 디자인에 맞는 weather icon으로 converting 하는 함수
    for source, dest in WEATHER_ICON_SET:
        if orig_url.endswith(source):
            return WEATHER_ICON_PATH + dest
    # 만약 아라에 적절한 아이콘이 없을 경우 앞에 http://www.google.com을 붙여 줌(기본 아이콘 사용)
    return "http://www.google.com" + orig_url
