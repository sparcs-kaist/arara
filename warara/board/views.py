# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator

import arara
import math


def index(request):
    rendered = render_to_string('board/index.html', {})
    return HttpResponse(rendered)


def list(request, board_name):
    r = {}
    server = arara.get_server()
    if "arara_session_key" in request.session:
        sess = request.session["arara_session_key"]
        r['logged_in'] = True
    else:
        sess = ""
        r['logged_in'] = False
    page_no = request.GET.get('page_no', 1)
    page_no = int(page_no)
    page_range_length = 10
    page_range_no = math.ceil(float(page_no) / page_range_length)
    ret, article_list = server.article_manager.article_list(sess, board_name, page_no)
    assert ret, article_list
    r['article_list'] = article_list
    r['board_name'] = board_name

    #pagination
    r['next'] = 'a'
    r['prev'] = 'a'
    r['next_group'] = 'a'
    r['prev_group'] = 'a'
    r['page_num'] = article_list.pop()['last_page']
    page_o = Paginator([x+1 for x in range(r['page_num'])],10)
    r['page_list'] = page_o.page(page_range_no).object_list
    if page_o.page(page_range_no).has_next():
        r['next_page_group'] = {'mark':r['next'], 'no':page_o.page(page_o.next_page_number()).start_index()}
        r['last_page'] = {'mark':r['next_group'], 'no':r['page_num']}
    if page_o.page(page_range_no).has_previous():
        r['prev_page_group'] = {'mark':r['prev'], 'no':page_o.page(page_o.previous_page_number()).end_index()}
        r['first_page'] = {'mark':r['prev_group'], 'no':1}

    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

def write(request, board_name):
    if request.POST:
        return write_(request, board_name)

    r = {}
    r['logged_in'] = True
    article_id = request.GET.get('article_id', 0)
    r['t_write'] = 'write'

    if article_id:
        server = arara.get_server()
        sess = request.session["arara_session_key"]
        ret, article_list = server.article_manager.read(sess, board_name, int(article_id))
        r['default_title'] = article_list[0]['title']
        r['default_text'] = article_list[0]['content']
        r['t_write'] = 'modify'
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
    assert ret, article_id

    if not ret:
        r['e'] = article_id
        rendered = render_to_string('board/error.html', r)
        return HttpResponse(rendered)

    return HttpResponseRedirect('/board/%s' % board_name)

def read(request, board_name, article_id):
    server = arara.get_server()
    r = {}
    sess = request.session["arara_session_key"]
    r['logged_in'] = True
    ret, article_list = server.article_manager.read(sess, board_name, int(article_id))
    assert ret, article_list
    """
    if not ret:
        r['e'] = article_list
        rendered = render_to_string('board/error.html', r)
        return HttpResponse(rendered)
        """

    r['article_list'] = article_list
    r['board_name'] = board_name
    username = request.session['arara_username']

    for article in article_list:
        if article['author_username'] == username:
            article['flag_modify'] = 1
        else:
            article['flag_modify'] = 0

    rendered = render_to_string('board/read.html', r)
    return HttpResponse(rendered)


def reply(request, board_name, article_id):
    server = arara.get_server()
    r = {}
    sess = request.session["arara_session_key"]
    r['logged_in'] = True
    reply_dic = {}
    reply_dic['content'] = request.POST.get('content', '')
    reply_dic['title'] = request.POST.get('title', '')
    root_id = request.POST.get('root_id', '')

    ret, no = server.article_manager.write_reply(sess, board_name, int(article_id), reply_dic)
    assert ret, article_list

    return HttpResponseRedirect('/board/%s/%s/' % (board_name, str(root_id)))

def vote(request, board_name, root_id, article_no):
    server = arara.get_server()
    sess = request.session['arara_session_key']
    server.vote_article(sess, board_name, int(article_no))

    return HttpResponseRedirect('/board/%s/%s' % (board_name, root_id))
