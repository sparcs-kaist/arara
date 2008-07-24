# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import arara


def index(request):
    rendered = render_to_string('board/index.html', {})
    return HttpResponse(rendered)


def list(request, board_name):
    server = arara.get_server()
    if "arara_session_key" in request.session:
        sess = request.session["arara_session_key"]
    else:
        sess = ""
    ret, article_list = server.article_manager.article_list(sess, board_name)
    r = {}
    r['article_list'] = article_list
    r['t_write'] = 'write'
    r['t_list'] = 'list'
    r['board_name'] = board_name

    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

def write(request, board_name):
    
    if request.POST:
        return write_(request, board_name)

    r = {}
    r['t_submit'] = 'write' #template_submit
    r['t_cancel'] = 'cancel'
    r['t_preview'] = 'preview'
    r['default_title'] = ''
    r['default_text'] = ''
    r['board_name'] = board_name

    rendered = render_to_string('board/write.html', r)
    return HttpResponse(rendered)

def write_(request, board_name):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    article_dic = {}
    r = {}
    r['url'] = ''.join(['/board/', board_name, '/'])
    article_dic['content'] = request.POST.get('text', '')
    article_dic['title'] = request.POST.get('title', '')
    ret, article_id = server.article_manager.write_article(sess, board_name, article_dic)

    if not ret:
        r['e'] = article_id
        rendered = render_to_string('board/error.html', r)
        return HttpResponse(rendered)

    return HttpResponseRedirect('/board/%s' % board_name)

def read(request, board_name, article_id):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    ret, article_list = server.article_manager.read(sess, board_name, int(article_id))
    r = {}
    if not ret:
        r['e'] = article_list
        rendered = render_to_string('board/error.html', r)
        return HttpResponse(rendered)

    r['article_list'] = article_list
    r['t_reply_write'] = 'reply'
    r['board_name'] = board_name

    rendered = render_to_string('board/read.html', r)
    return HttpResponse(rendered)


def reply(request, board_name, article_id):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    reply_dic = {}
    reply_dic['content'] = request.POST.get('content', '')
    reply_dic['title'] = request.POST.get('title', '')
    root_id = request.POST.get('root_id', '')

    ret, no = server.article_manager.write_reply(sess, board_name, int(article_id), reply_dic)

    return HttpResponseRedirect('/board/%s/%s/' % (board_name, str(root_id)))
