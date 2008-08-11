# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator

from thirdparty.postmarkup import render_bbcode

import os
import arara
import math
import warara

def index(request):
    rendered = render_to_string('board/index.html', {})
    return HttpResponse(rendered)

def list(request, board_name):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    page_no = request.GET.get('page_no', 1)
    page_no = int(page_no)
    page_range_length = 10
    page_range_no = math.ceil(float(page_no) / page_range_length)
    ret, article_result = server.article_manager.article_list(sess, board_name, page_no)
    assert ret, article_result
    article_list = article_result['hit']
    ret, board_dict = server.board_manager.get_board(board_name)
    assert ret, board_dict
    for i in range(len(article_list)):
        if article_list[i].get('deleted', 0):
            article_list[i]['title'] = 'deleted'
            article_list[i]['author_username'] = 'deleted'

        max_length = 15 # max title string length
        if len(article_list[i]['title']) > max_length:
            article_list[i]['title'] = article_list[i]['title'][0:max_length]
            article_list[i]['title'] += "..."

    r['board_name'] = board_dict['board_name']
    r['board_description'] = board_dict['board_description']
    r['article_list'] = article_list
    r['search_method_list'] = [{'val':'all', 'text':'all'}, {'val':'title', 'text':'title'},
            {'val':'content', 'text':'content'},
            {'val':'author_nick', 'text':'nickname'}, {'val':'author_username', 'text':'id'}]

    #pagination
    r['next'] = 'a'
    r['prev'] = 'a'
    r['next_group'] = 'a'
    r['prev_group'] = 'a'
    r['page_num'] = article_result['last_page']
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
    if request.method == 'POST':
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
        r['article_no'] = article_list[0]['id']
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
    if request.POST.get('write_type', 0) == 'modify':
        article_no = request.POST.get('article_no', 0)
        ret, article_id = server.article_manager.modify(sess, board_name, int(article_no), article_dic)
    else:
        ret, article_id = server.article_manager.write_article(sess, board_name, article_dic)
    assert ret, article_id
    
    #upload file
    
    if request.FILES:
        for key, file in request.FILES.items():
            ret, file_path, file_name = server.file_manager.save_file(sess, int(article_id), file.name)
            assert ret, file_path
            if not os.path.isdir('files/%s' % file_path):
                os.makedirs('files/%s' % file_path)
            fp = open('files/%s/%s' % (file_path, file_name), 'wb')
            fp.write(file.read())

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

    for i in range(len(article_list)):
        article_list[i]['content'] = render_bbcode(article_list[i]['content'], 'UTF-8')
        if article_list[i]['deleted']:
            article_list[i]['author_username'] = 'deleted'
            article_list[i]['content'] = 'deleted'
            article_list[i]['title'] = 'deleted'

    r['article_list'] = article_list
    r['board_name'] = board_name
    username = request.session['arara_username']
    ret, list = server.board_manager.get_board_list()

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

    ret, article_id = server.article_manager.write_reply(sess, board_name, int(article_id), reply_dic)
    assert ret, article_list

    #upload file
    
    if request.FILES:
        for key, file in request.FILES.items():
            ret, file_path, file_name = server.file_manager.save_file(sess, int(article_id), file.name)
            if not os.path.isdir('files/%s' % file_path):
                os.makedirs('files/%s' % file_path)
            fp = open('files/%s/%s' % (file_path, file_name), 'wb')
            fp.write(file.read())

    return HttpResponseRedirect('/board/%s/%s/' % (board_name, str(root_id)))

def vote(request, board_name, root_id, article_no):
    server = arara.get_server()
    sess = request.session['arara_session_key']
    ret, message = server.article_manager.vote_article(sess, board_name, int(article_no))
    assert ret, message

    return HttpResponseRedirect('/board/%s/%s' % (board_name, root_id))

def delete(request, board_name, root_id, article_no):
    server = arara.get_server()
    sess = request.session['arara_session_key']
    ret, message = server.article_manager.delete(sess, board_name, int(article_no))
    assert ret, message

    return HttpResponseRedirect('/board/%s/%s' % (board_name, root_id))

def search(request, board_name):
    server = arara.get_server()
    sess = request.session['arara_session_key']

    search_word = request.GET.get('search_word', '')
    search_method = request.GET.get('search_method', 'all')
    page_no = request.GET.get('page_no', 1)
    page_no = int(page_no)
    if page_no:
        page_no = 1
    page_length = 20
    page_range_length = 10
    page_range_no = math.ceil(float(page_no) / page_range_length)

    ret, search_result = server.article_manager.search(sess, board_name, search_word, search_method, page_no, page_length)
    assert ret, search_result
    r = {'logged_in':True}
    r['article_list'] = search_result['hit']
    r['page_num'] = search_result.get('last_page', 1)
    r['search_time'] = search_result.get('search_time', 1)
    r['article_num'] = search_result['results']
    r['search_method_list'] = [{'val':'all', 'text':'all'}, {'val':'title', 'text':'title'},
            {'val':'content', 'text':'content'},
            {'val':'author_nick', 'text':'nickname'}, {'val':'author_username', 'text':'id'}]
    r['search_method'] = search_method

    ret, board_dict = server.board_manager.get_board(board_name)
    assert ret, board_dict
    for i in range(len(r['article_list'])):
        if r['article_list'][i].get('deleted', 0):
            r['article_list'][i]['title'] = 'deleted'
            r['article_list'][i]['author_username'] = 'deleted'

        max_length = 15 # max title string length
        if len(r['article_list'][i]['title']) > max_length:
            r['article_list'][i]['title'] = r['article_list'][i]['title'][0:max_length]
            r['article_list'][i]['title'] += "..."

    r['board_name'] = board_dict['board_name']
    r['board_description'] = board_dict['board_description']

    #pagination
    r['next'] = 'a'
    r['prev'] = 'a'
    r['next_group'] = 'a'
    r['prev_group'] = 'a'
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

def wrap_error(f):
    def check_error(*args, **argv):
        r = {} #render item
        try:
            return f(*args, **argv)
        except AssertionError, e:
            if e.message == "NOT_LOGGED_IN":
                r['error_message'] = "not logged in!"
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)
            elif e.message == "ALEADY_LOGGED_IN":
                r['error_message'] = "aleady logged in"
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)

            r['error_message'] = "unknown keyerror : " + repr(e.message)
            rendered = render_to_string("error.html", r)
            return HttpResponse(rendered)
                
        except KeyError, e:
            if e.message == "arara_session_key":
                r['error_message'] = "not logged in!"
                rendered = render_to_string("error.html", r)
                return HttpResponse(rendered)
            
            r['error_message'] = "unknown keyerror : " + repr(e.message)
            rendered = render_to_string("error.html", r)
            return HttpResponse(rendered)

    return check_error

#list = wrap_error(list)
read = wrap_error(read)
vote = wrap_error(vote)
write = wrap_error(write)
reply = wrap_error(reply)
delete = wrap_error(delete)
search = wrap_error(search)
