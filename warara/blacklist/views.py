from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from arara_thrift.ttypes import *

import arara
import warara


def get_various_info(request):
    server = arara.get_server()
    sess = test.login()
    r['num_blacklist_member'] = 0
    return r

@warara.wrap_error
def add(request):
    if request.method == 'POST':
        blacklist_id = request.POST['blacklist_id']
        server = arara.get_server()
        sess = request.session["arara_session_key"]
        id_converting = server.member_manager.search_user(sess, blacklist_id, "") 
        converted_id =  id_converting[0].username
        server.blacklist_manager.add(sess, converted_id, True, True) 
        if request.POST.get('ajax', 0):
            return HttpResponse(1)
        return HttpResponseRedirect("/blacklist/")
    else:
        return HttpResponse('Must use POST')

@warara.wrap_error
def delete(request):
    if request.method == 'POST':
        username = request.POST['username']
        server = arara.get_server()
        sess = request.session["arara_session_key"]
        server.blacklist_manager.delete(sess, username)
        return HttpResponseRedirect("/blacklist/")

@warara.wrap_error
def update(request):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    blacklist = server.blacklist_manager.list_(sess)
    bl_submit_chooser = request.POST['bl_submit_chooser']
    if bl_submit_chooser == "update":
        for b in blacklist:
            article_bl_key = 'blacklist_article_%s' % b.blacklisted_user_username
            if article_bl_key in request.POST:
                b.block_article = True
            else:
                b.block_article = False
            message_bl_key = 'blacklist_message_%s' % b.blacklisted_user_username
            if message_bl_key in request.POST:
                b.block_message = True
            else:
                b.block_message = False

            server.blacklist_manager.modify(sess, BlacklistRequest(
                blacklisted_user_username = b.blacklisted_user_username,
                block_article = b.block_article,
                block_message = b.block_message))
    if bl_submit_chooser == "delete":
        for b in blacklist:
            delete_user = request.POST.get('bl_%s_delete' % b.blacklisted_user_username, "")
            if delete_user != "":
                server.blacklist_manager.delete_(sess, delete_user)

    return HttpResponseRedirect("/blacklist/")

@warara.wrap_error
def index(request):
    server = arara.get_server()
    r = {}
    sess = request.session["arara_session_key"]
    r['logged_in'] = True
    blacklist = server.blacklist_manager.list_(sess)
    r['blacklist'] = blacklist

    if 'search' in request.GET:
        search_user_info = request.GET['search']
        user_id = server.member_manager.search_user(sess, search_user_info, "")
        r['search_result'] = user_id

    rendered = render_to_string('blacklist/index.html', r)
    return HttpResponse(rendered)
