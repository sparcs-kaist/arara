# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.cache import cache

from thirdparty.postmarkup import render_bbcode

from arara_thrift.ttypes import *

import os
import arara
import math
import datetime
import warara

from arara.settings import FILE_DIR, FILE_MAXIMUM_SIZE

@warara.wrap_error
def index(request):
    rendered = render_to_string('board/index.html', {})
    return HttpResponse(rendered)

def get_article_list(request, r, mode):
    server = arara.get_server()
    sess, _ = warara.check_logged_in(request)
    
    page_no = request.GET.get('page_no', 1)
    try:
        # Some crawlbot access to /?page_no= (missing page number)
        # So we have to handle such case ...
        r['page_no'] = int(page_no)
    except Exception:
        raise InvalidOperation("Wrong Pagenumber")
    if not r.get('selected_method_list', 0):
        r['selected_method_list'] = ['title', 'content', 'author_nickname', 'author_username']
        r['search_method_list'] = [{'val':'title', 'text':'title'}, {'val':'content', 'text':'content'},
                {'val':'author_nickname', 'text':'nickname'}, {'val':'author_username', 'text':'id'}]
        
    page_length = 20
    if mode == 'list':
        article_result = server.article_manager.article_list(sess, r['board_name'], r['page_no'], 20)
    elif mode == 'read':
        article_result = server.article_manager.article_list_below(sess, r['board_name'], int(r['article_id']), 20)
        r['page_no'] = article_result.current_page
    elif mode == 'search':
        page_no = int(page_no)
        for k, v in r['search_method'].items():
            del r['search_method'][k]
            r['search_method'][str(k)] = v
        search_method = SearchQuery(**r['search_method'])
        article_result = server.search_manager.search(sess, False, r['board_name'], search_method, page_no, page_length)

    page_range_length = 10
    page_range_no = math.ceil(float(page_no) / page_range_length)

    article_list = article_result.hit
    for i in range(len(article_list)):
        if article_list[i].deleted:
            article_list[i].title = '-- Deleted --'
            article_list[i].author_username = ''

    for article in article_list:
        article.date = datetime.datetime.fromtimestamp(article.date)

    r['article_list'] = article_list
    for i, smi in enumerate(r['search_method_list']):
        if smi['val'] in r['selected_method_list']:
            r['search_method_list'][i]['selected'] = True
        else:
            r['search_method_list'][i]['selected'] = False

    #pagination
    r['next'] = '〉'
    r['prev'] = '〈'
    r['next_group'] = '》'
    r['prev_group'] = '《'
    r['page_num'] = article_result.last_page
    page_o = Paginator([x+1 for x in range(r['page_num'])],10)
    r['page_list'] = page_o.page(page_range_no).object_list
    if page_o.page(page_range_no).has_next():
        r['next_page_group'] = {'mark':r['next'], 'no':page_o.page(page_o.page(page_range_no).next_page_number()).start_index()}
        r['last_page'] = {'mark':r['next_group'], 'no':r['page_num']}
    if page_o.page(page_range_no).has_previous():
        r['prev_page_group'] = {'mark':r['prev'], 'no':page_o.page(page_o.page(page_range_no).previous_page_number()).end_index()}
        r['first_page'] = {'mark':r['prev_group'], 'no':1}

    #read_only_control
    board_dict = server.board_manager.get_board(r['board_name'])
    r['board_dict'] = board_dict

@warara.wrap_error
def list(request, board_name):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    r['board_name'] = board_name
    get_article_list(request, r, 'list')

    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def write(request, board_name):
    server = arara.get_server()
    if request.method == 'POST':
        return write_(request, board_name)

    if request.GET.get('multi', 0):
        sess, r = warara.check_logged_in(request)
        rec_num = request.GET['multi']
        article_dic={'title':'test title', 'content':'test content'}
        for i in range(int(rec_num)):
            article_id = server.article_manager.write_article(sess, board_name, WrittenArticle(**article_dic))

        return HttpResponseRedirect('../')

    sess, r = warara.check_logged_in(request)
    article_id = request.GET.get('article_id', 0)
    r['t_write'] = 'write'
    user_info = server.member_manager.get_info(sess)
    r['default_text'] = user_info.signature

    if article_id:
        sess = request.session["arara_session_key"]
        article_list = server.article_manager.read(sess, board_name, int(article_id))
        r['default_title'] = article_list[0].title
        r['default_text'] = article_list[0].content
        r['article_no'] = article_list[0].id
        r['t_write'] = 'modify'
        r['article'] = article_list[0]
    r['board_name'] = board_name

    rendered = render_to_string('board/write.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def write_(request, board_name):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    article_dic = {}
    r['url'] = ''.join(['/board/', board_name, '/'])
    article_dic['content'] = request.POST.get('text', '')
    article_dic['title'] = request.POST.get('title', '')
    if request.POST.get('write_type', 0) == 'modify':
        article_no = request.POST.get('article_no', 0)
        article_id = server.article_manager.modify(sess, board_name, int(article_no), WrittenArticle(**article_dic))

        delete_file = request.POST.get('delete_file', 0) #delete_file
        if delete_file:
            delete_file = delete_file[1:]
            delete_file = delete_file.split('&')
            for file_id in delete_file:
                file = server.file_manager.delete_file(sess, int(article_no), int(file_id))
                os.remove("%s/%s/%s" % (FILE_DIR, file.file_path, file.saved_filename))

    else:
        article_id = server.article_manager.write_article(sess, board_name, WrittenArticle(**article_dic))
    
    #upload file
    if request.FILES:
        file = {}
        for key, file_ob in request.FILES.items():
            if file_ob.size > FILE_MAXIMUM_SIZE:
                continue
            file = server.file_manager.save_file(sess, int(article_id), file_ob.name)
            if not os.path.isdir('%s/%s' % (FILE_DIR, file.file_path)):
                os.makedirs('%s/%s' % (FILE_DIR, file.file_path))
            fp = open('%s/%s/%s' % (FILE_DIR, file.file_path, file.saved_filename), 'wb')

            fp.write(file_ob.read())

    return HttpResponseRedirect('/board/%s/%s' % (board_name, str(article_id)))

@warara.wrap_error
def read(request, board_name, article_id):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    article_list = server.article_manager.read(sess, board_name, int(article_id))
    image_filetype = ['jpg', 'jpeg', 'gif', 'png']
    for article in article_list:
        article.date = datetime.datetime.fromtimestamp(article.date)

    for i in range(len(article_list)):
        if 'attach' in article_list[i].__dict__ and article_list[i].attach: #image view
            article_list[i].__dict__['image'] = []
            insert_image_tag_list = article_list[i].__dict__['image']
            for file in article_list[i].attach:
                if file.filename.split('.')[-1].lower() in image_filetype:
                    insert_image_tag = "<p><img src=\"/board/%s/%d/%d/file/%d/\"></img></p>" % (board_name, article_list[i].root_id, article_list[i].id, file.file_id)
                    insert_image_tag_list.append(insert_image_tag)

        #article_list[i]['content'] = render_bbcode(article_list[i]['content'], 'UTF-8')
        if article_list[i].deleted: #deleted article access
            article_list[i].author_nickname = ''
            article_list[i].author_username = ''
            article_list[i].content = 'deleted'
            article_list[i].title = 'deleted'
            article_list[i].attach = None
            article_list[i].image = None
        if article_list[i].depth > 12: #set depth 12 which has bigger depth than 12
            article_list[i].depth = 12
        article_list[i].depth_list = [x+1 for x in range(article_list[i].depth-2)]

        # Finally, render the content using content renderer
        article_list[i].content = render_content(article_list[i].content)

    r['board_name'] = board_name
    username = request.session['arara_username']
    r['article_id'] = article_id
    r['default_text'] = server.member_manager.get_info(sess)
    r['default_text'] = r['default_text'].signature

    for article in article_list:
        if article.author_username == username:
            article.flag_modify = 1
        else:
            article.flag_modify = 0
    r['article_read_list'] = article_list

    #article_below_list
    get_article_list(request, r, 'read')

    rendered = render_to_string('board/read.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def reply(request, board_name, article_id):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    reply_dic = {}
    reply_dic['content'] = request.POST.get('content', '')
    reply_dic['title'] = request.POST.get('title', '')
    root_id = request.POST.get('root_id', '')

    article_id = server.article_manager.write_reply(sess, board_name, int(article_id), WrittenArticle(**reply_dic))

    #upload file
    if request.FILES:
        file = {}
        for key, file_ob in request.FILES.items():
            file = server.file_manager.save_file(sess, int(article_id), file_ob.name)
            if not os.path.isdir('%s/%s' % (FILE_DIR, file.file_path)):
                os.makedirs('%s/%s' % (FILE_DIR, file.file_path))
            fp = open('%s/%s/%s' % (FILE_DIR, file.file_path, file.saved_filename), 'wb')
            fp.write(file_ob.read())

    return HttpResponseRedirect('/board/%s/%s/' % (board_name, str(root_id)))

@warara.wrap_error
def vote(request, board_name, root_id, article_no):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    try:
        server.article_manager.vote_article(sess, board_name, int(article_no))
    except InvalidOperation, e:
        return HttpResponse("ALREADY_VOTED")

    return HttpResponse("OK")

@warara.wrap_error
def delete(request, board_name, root_id, article_no):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request)
    server.article_manager.delete_(sess, board_name, int(article_no))

    return HttpResponseRedirect('/board/%s/%s' % (board_name, root_id))

@warara.wrap_error
def search(request, board_name):
    server = arara.get_server()
    sess, r = warara.check_logged_in(request);
    r['board_name'] = board_name

    r['selected_method_list'] = ['title', 'content', 'author_nickname', 'author_username']
    r['search_method_list'] = [{'val':'title', 'text':'title'}, {'val':'content', 'text':'content'},
            {'val':'author_nickname', 'text':'nickname'}, {'val':'author_username', 'text':'id'}]
    search_word = request.GET.get('search_word', '')
    r['selected_method_list'] = []

    r['chosen_search_method'] = request.GET.get('chosen_search_method', '')
    if r['chosen_search_method']:
        r['search_method'] = dict(zip(r['chosen_search_method'].split('|'), [search_word for x in range(100)]))
        r['selected_method_list'] = r['chosen_search_method'].split('|')
    else:
        r['search_method'] = {}
        for method in r['search_method_list']:
            if request.GET.get(method['val'], 0):
                r['chosen_search_method'] = r['chosen_search_method'] + '|' + method['val']
                r['selected_method_list'].append(method['val'])
                r['search_method'][method['val']] = search_word
        r['chosen_search_method'] = r['chosen_search_method'].strip('|')
    get_article_list(request, r, 'search')

    r['method'] = 'search'
    path = request.get_full_path()
    path = path.split('?')[0]
    r['path'] = path + "?search_word=" + search_word + "&chosen_search_method=" + r['chosen_search_method']
    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def file_download(request, board_name, article_root_id, article_id, file_id):
    server = arara.get_server()
    file = {}
    file= server.file_manager.download_file(int(article_id), int(file_id))
    file_ob = open("%s/%s/%s" % (FILE_DIR, file.file_path, file.saved_filename))

    response = HttpResponse(file_ob, mimetype="application/x-forcedownload")
    response['Content-Disposition'] = "attachment; filename=" + unicode(file.real_filename).encode('cp949', 'replace')
    return response

# Using Django's default HTML handling util, escape all tags and urlize
from django.utils import html
def render_content(content):
    return html.urlize(html.escape(content))
