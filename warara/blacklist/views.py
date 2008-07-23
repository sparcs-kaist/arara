from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import arara

def test_login():
    server = arara.get_server()
    ret, sess = server.login_manager.login('breadfish', 'breadfish', '127.0.0.1')
    assert ret == True, sess
    return sess

def get_various_info(request):
    server = arara.get_server()
    sess = test.login()
    r['num_blacklist_member'] = 0
    return r

def add(request):
    if request.method == 'POST':
        blacklist_id = request.POST['blacklist_id']
        server = arara.get_server()
        sess = test_login()
        ret, message = server.blacklist_manager.add(sess, blacklist_id)
        assert ret, message
        return HttpResponseRedirect("/blacklist/")
    else:
        return HttpResponse('Must use POST')

def delete(request):
    if request.method == 'POST':
        username = request.POST['username']
        server = arara.get_server()
        sess = test_login()
        ret, message = server.blacklist_manager.delete(sess, username)
        assert ret, message
        return HttpResponseRedirect("/blacklist/")


def update(request):
    server = arara.get_server()
    sess = test_login()
    ret, blacklist = server.blacklist_manager.list(sess)
    for b in blacklist:
        article_bl_key = 'blacklist_article_%s' % b['username']
        if article_bl_key in request.POST:
            b['block_article'] = True
        else:
            b['block_article'] = False
        message_bl_key = 'blacklist_message_%s' % b['username']
        if message_bl_key in request.POST:
            b['block_message'] = True
        else:
            b['block_message'] = False

        ret, msg = server.blacklist_manager.modify(sess, b)
        assert ret, msg

    return HttpResponseRedirect("/blacklist/")


def index(request):
    server = arara.get_server()
    sess = test_login()
    r = {}
    ret, blacklist = server.blacklist_manager.list(sess)
    r['blacklist'] = blacklist

    if 'search' in request.GET:
        query = request.GET['search']
        search_type = 'username'
        if 'search_type' in request.GET:
            search_type = request.GET['search_type']
        search_user_info = {search_type: query}
        ret, user_id = server.member_manager.search_user(sess, search_user_info)
        if ret:
            r['search_result'] = user_id

    rendered = render_to_string('blacklist/index.html', r)
    return HttpResponse(rendered)
