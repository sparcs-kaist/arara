# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.cache import cache

from thirdparty.postmarkup import render_bbcode

from arara_thrift.ttypes import *

import os
import datetime
import warara
from warara import warara_middleware

from etc.warara_settings import FILE_DIR, FILE_MAXIMUM_SIZE

IMAGE_FILETYPE = ['jpg', 'jpeg', 'gif', 'png']

@warara.wrap_error
def index(request):
    rendered = render_to_string('board/index.html', {})
    return HttpResponse(rendered)

def get_article_list(request, r, mode):
    """
    글 목록을 Backend 로부터 받아온다.

    @type  request: Django request
    @param request: Django 로 넘어온 Request
    @type  r: dict
    @param r: 차후 render_to_string 에 넘겨질 dictionary
    @type  mode: string
    @param mode: 작동방식 - 크게 list, read, search 가 있음
    """
    server = warara_middleware.get_server()
    sess, _ = warara.check_logged_in(request)
    
    # 현재 읽고자 하는 page 의 번호를 알아낸다.
    page_no = request.GET.get('page_no', 1)
    # 가끔 일부 crawlbot 이 "/?page_no=" 라는 주소로 접근. page number 가 "" 가 된다.
    # 이런 경우들에 대한 일반적인 예외 처리를 한다.
    # XXX 2010.05.18: InvalidOperation 을 내뱉는 것이 능사인지 생각해보자.
    try:
        page_no = int(page_no)
        r['page_no'] = page_no
    except Exception:
        raise InvalidOperation("Wrong Pagenumber")
    # XXX 2010.05.18: page_no 가 가끔 0 으로 들어오는 때가 있다.
    #                 Warara 코드의 문제인 경우조차 있어서, 일단 그럴땐 1 로 설정해주자.
    if page_no < 0:
        raise InvalidOperation("Wrong Pagenumber")
    elif page_no == 0:
        page_no = 1

    if not r.get('selected_method_list', 0):
        r['selected_method_list'] = ['title', 'content', 'author_nickname', 'author_username']
        r['search_method_list'] = [{'val':'title', 'text':'title'}, {'val':'content', 'text':'content'},
                {'val':'author_nickname', 'text':'nickname'}, {'val':'author_username', 'text':'id'}]
        
    # XXX 2010.05.18. page_length 변수를 사용하지 않던 걸 사용하도록 고치다.
    #                 이 값은 Backend 에서 가져오는 페이지당 글의 갯수이다.
    #                 article_per_page 정도가 적당하다. 나중에 이름을 바꾸자.
    page_length = 20
    if mode == 'list':
        #TODO: heading 과 include_all_headings
        article_result = server.article_manager.article_list(sess, r['board_name'], u"", page_no, page_length, True)
    elif mode == 'read':
        #TODO: heading 과 include_all_headings
        article_result = server.article_manager.article_list_below(sess, r['board_name'], u"", int(r['article_id']), page_length, True)
        r['page_no'] = article_result.current_page
    elif mode == 'search':
        for k, v in r['search_method'].items():
            del r['search_method'][k]
            r['search_method'][str(k)] = v
        search_method = SearchQuery(**r['search_method'])
        #TODO: heading 과 include_all_headings
        article_result = server.search_manager.search(sess, False, r['board_name'], u"", search_method, page_no, page_length, True)

    # XXX 2010.05.18. page_range_length 는 글 목록 하단에 표시하는 page 들의 갯수이다.
    page_range_length = 10

    # XXX 2010.05.18. page_range_no 는 현 page 가 글 목록 하단의 page 들 중 몇 째인가이다.
    page_range_no = page_no / page_range_length
    if page_no % page_range_length > 0:
        page_range_no += 1

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
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    r['board_name'] = board_name
    get_article_list(request, r, 'list')

    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def write(request, board_name):
    server = warara_middleware.get_server()
    if request.method == 'POST':
        return write_(request, board_name)

    if request.GET.get('multi', 0):
        sess, r = warara.check_logged_in(request)
        rec_num = request.GET['multi']
        article_dic={'title':'test title', 'content':'test content', 'heading': u''}
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
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    article_dic = {}
    r['url'] = ''.join(['/board/', board_name, '/'])
    article_dic['content'] = request.POST.get('text', '')
    article_dic['title'] = request.POST.get('title', '')
    article_dic['heading'] = request.POST.get('heading', '') # Heading !!!
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
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    article_list = server.article_manager.read(sess, board_name, int(article_id))
    username = request.session['arara_username']
    userid = request.session['arara_userid']

    for article in article_list:
        article.date = datetime.datetime.fromtimestamp(article.date)

        if article.deleted: #deleted article access
            article.author_nickname = ''
            article.author_username = ''
            article.content = '-- deleted --'
            article.title  = '-- deleted --'
            article.attach = None
            article.image = None
            continue

        if article.__dict__.has_key('attach') and article.attach: #image view
            insert_image_tag_list = []
            for file in article.attach:
                if file.filename.split('.')[-1].lower() in IMAGE_FILETYPE:
                    insert_image_tag = "<p><img src=\"/board/%s/%d/%d/file/%d/\"></img></p>" % (board_name, article.root_id, article.id, file.file_id)
                    insert_image_tag_list.append(insert_image_tag)
            article.__dict__['image'] = insert_image_tag_list

        #article['content'] = render_bbcode(article_list[i]['content'], 'UTF-8')

        if article.depth > 12: #set depth 12 which has bigger depth than 12
            article.depth = 12
        article.depth_list = range(1, article.depth - 1)

        # Finally, render the content using content renderer
        article.content = render_content(article.content)

        if article.author_id == userid:
            article.flag_modify = 1
        else:
            article.flag_modify = 0

    r['board_name'] = board_name
    r['article_id'] = article_id
    r['default_text'] = server.member_manager.get_info(sess)
    r['default_text'] = r['default_text'].signature
    r['article_read_list'] = article_list
    r['root_article'] = article_list[0]

    #article_below_list
    get_article_list(request, r, 'read')

    rendered = render_to_string('board/read.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def reply(request, board_name, article_id):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    reply_dic = {}
    reply_dic['content'] = request.POST.get('content', '')
    reply_dic['title'] = request.POST.get('title', '')
    reply_dic['heading'] = request.POST.get('heading', '') # TODO: HEADING !!
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
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    try:
        server.article_manager.vote_article(sess, board_name, int(article_no))
    except InvalidOperation, e:
        return HttpResponse("ALREADY_VOTED")

    return HttpResponse("OK")

@warara.wrap_error
def delete(request, board_name, root_id, article_no):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    server.article_manager.delete_(sess, board_name, int(article_no))

    return HttpResponseRedirect('/board/%s/%s' % (board_name, root_id))

def destroy(request, board_name, root_id, article_no):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    server.article_manager.destroy_article(sess, board_name, int(article_no))
    # XXX 2010.05.14.
    # 글을 destroy하였으므로 해당 보드로 돌아간다.
    # 추후에는 pageno 정보를 이용하도록 수정하는 게 좋겠다.
    # 어차피 지금은 SYSOP 이 아니면 이 작업을 할 수 없지만.
    return HttpResponseRedirect('/board/%s' % board_name)
    # XXX 여기까지.

@warara.wrap_error
def search(request, board_name):
    server = warara_middleware.get_server()
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
    # XXX 2010.05.14.
    #  바로 다음 줄의 request.get_full_path() 를 호출하면 이상하게도 utf-8 error 가 발생한다. 한글로 검색했을 때 주로 발생하는데, 문제의 재현이 쉽지 않다. 어떤 땐 utf-8 error 가 나고, 어떤 땐 안 난다.
    # XXX 여기까지.
    path = request.get_full_path()
    path = path.split('?')[0]
    r['path'] = path + "?search_word=" + search_word + "&chosen_search_method=" + r['chosen_search_method']
    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def file_download(request, board_name, article_root_id, article_id, file_id):
    server = warara_middleware.get_server()
    file = {}
    file= server.file_manager.download_file(int(article_id), int(file_id))
    file_ob = open("%s/%s/%s" % (FILE_DIR, file.file_path, file.saved_filename))

    response = HttpResponse(file_ob, mimetype="application/x-forcedownload")
    response['Content-Disposition'] = "attachment; filename=" + unicode(file.real_filename).encode('cp949', 'replace')
    # Django's never_cache decorator causes empty file, so we do it manually.
    # NOTE: Django's cache warara_middleware uses cache backends with timeout value from http headers
    #       with simultaneously setting appropriate http headers to control web browsers.
    response['Cache-Control'] = 'max-age=0, no-cache=True'
    return response

# Using Django's default HTML handling util, escape all tags and urlize
# 동시에 <a> tag 를 target="_blank" 로 설정되도록 regex 를 써서 바꿔버린다.
# TODO: 더 나은 방법이 있다면 (CSS 에 a tag 에 속성 먹이기가 더 예쁘지 않을까...전체를 div class 로 감싸서)
#       그거로 바꾸기!
from django.utils import html
import re
a_tag = re.compile(r'<a href="(.+?)">')
def render_content(content):
    return a_tag.sub(r'<a href="\1" target="_blank">', html.urlize(html.escape(content)))
