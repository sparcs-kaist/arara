from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from arara_thrift.ttypes import *

import arara


def get_various_info(request):
    server = arara.get_server()
    sess = test.login()
    r['num_blacklist_member'] = 0
    return r

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

def delete(request):
    if request.method == 'POST':
        username = request.POST['username']
        server = arara.get_server()
        sess = request.session["arara_session_key"]
        server.blacklist_manager.delete(sess, username)
        return HttpResponseRedirect("/blacklist/")

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

#index = wrap_error(index)
#get_various_info = wrap_error(get_various_info)
#add = wrap_error(add)
#delete = wrap_error(delete)
#update = wrap_error(update)
