# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.cache import cache

from arara_thrift.ttypes import *

import os
import datetime
import re
import mimetypes
import urllib
import warara
from warara import warara_middleware

from etc.warara_settings import FILE_DIR, FILE_MAXIMUM_SIZE
from etc import warara_settings

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
        r['search_method_list'] = [{'val':'title', 'text':'제목'}, {'val':'content', 'text':'본문'},
                {'val':'author_nickname', 'text':'글쓴이'}, {'val':'author_username', 'text':'ID'}]
        
    # XXX 2010.05.18. page_length 변수를 사용하지 않던 걸 사용하도록 고치다.
    #                 이 값은 Backend 에서 가져오는 페이지당 글의 갯수이다.
    #                 article_per_page 정도가 적당하다. 나중에 이름을 바꾸자.
    page_length = 20
    if mode == 'list':
        # GET 으로 넘어온 말머리가 있는지 본다.
        heading = request.GET.get('heading', None)
        if heading == None and 'page_no' in request.GET:
            if 'heading' in request.session:
                heading = request.session['heading']
        else:
            request.session['heading'] = heading
        include_all_headings = (heading == None)
        article_result = server.article_manager.article_list(sess, r['board_name'], heading, page_no, page_length, include_all_headings)
    elif mode == 'total_list':
        article_result = server.article_manager.article_list(sess, u"", u"", page_no, page_length, True)
    elif mode == 'read':
        #TODO: heading 과 include_all_headings
        if 'heading' in request.session:
            heading = request.session['heading']
        else:
            heading = None
        include_all_headings = (heading == None)
        article_result = server.article_manager.article_list_below(sess, r['board_name'], heading, int(r['article_id']), page_length, include_all_headings)
        r['page_no'] = article_result.current_page
    elif mode == 'total_read':
        article_result = server.article_manager.article_list_below(sess, u'', u'', int(r['article_id']), page_length, True)
        r['page_no'] = article_result.current_page
    elif mode == 'search':
        for k, v in r['search_method'].items():
            del r['search_method'][k]
            r['search_method'][str(k)] = v
        search_method = SearchQuery(**r['search_method'])
        heading = request.GET.get('search_heading', None)
        include_all_headings = (heading == None)
        article_result = server.search_manager.search(sess, False, r['board_name'], heading, search_method, page_no, page_length, include_all_headings)
    elif mode == 'total_search':
        for k, v in r['search_method'].items():
            del r['search_method'][k]
            r['search_method'][str(k)] = v
        search_method = SearchQuery(**r['search_method'])
        article_result = server.search_manager.search(sess, False, u'', u'', search_method, page_no, page_length, True) 

    # XXX 2010.05.18. page_range_length 는 글 목록 하단에 표시하는 page 들의 갯수이다.
    page_range_length = 10

    # XXX 2010.05.18. page_range_no 는 현 page 가 글 목록 하단의 page 들 중 몇 째인가이다.
    page_range_no = page_no / page_range_length
    if page_no % page_range_length > 0:
        page_range_no += 1

    article_list = article_result.hit
    for article in article_list:
        if article.deleted:
            article.title = '-- Deleted --'
            article.author_username = ''
        article.date = datetime.datetime.fromtimestamp(article.date)

    if not warara_settings.READ_STATUS_ENABLED:
        # 모든 글이 무조건 읽은 글로 표시되도록 한다
        for article in article_list:
            article.read_status = 'R'

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

    if mode == 'total_list' or mode == 'total_read' or mode == 'total_search':
        r['board_desc'] = u'All articles in ARA BBS!'
        r['have_heading'] = False
    else:
        #read_only_control
        board_dict = server.board_manager.get_board(r['board_name'])
        r['board_dict'] = board_dict
        r['board_desc'] = board_dict.board_description

        # heading control
        if len(board_dict.headings) == 0:
            r['have_heading'] = False
        else:
            r['have_heading'] = True
            r['board_heading_list'] = board_dict.headings
            r['default_heading'] = heading

@warara.wrap_error
def list(request, board_name):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    r['mode'] = 'board'
    r['board_name'] = board_name
    get_article_list(request, r, 'list')

    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def write(request, board_name):
    server = warara_middleware.get_server()
    if request.method == 'POST':
        return write_(request, board_name)

    sess, r = warara.check_logged_in(request)
    article_id = request.GET.get('article_id', 0)
    r['t_write'] = 'write'
    user_info = server.member_manager.get_info(sess)

    if article_id:
        sess = request.session["arara_session_key"]
        article_list = server.article_manager.read_article(sess, board_name, int(article_id))
        r['default_title'] = article_list[0].title
        r['default_heading'] = article_list[0].heading
        r['default_text'] = article_list[0].content
        r['article_no'] = article_list[0].id
        r['t_write'] = 'modify'
        r['article'] = article_list[0]
        r['modify'] = True
        r['root_id'] = article_list[0].root_id
    else:
        r['modify'] = False
    r['board_name'] = board_name

    # 시그 선택할 수 있도록 시그를 보여준다.
    r['user_signature'] = user_info.signature 

    # heading control
    board_dict = server.board_manager.get_board(board_name)
    if len(board_dict.headings) == 0:
        r['have_heading'] = False
        r['board_heading_list'] = []
    else:
        r['have_heading'] = True
        r['board_heading_list'] = board_dict.headings

    r['board_type'] = board_dict.type

    rendered = render_to_string('board/write.html', r)
    return HttpResponse(rendered)

def _upload_file(server, sess, article_id, FILES):
    '''
    파일을 업로드한다.
    '''
    file_list = sorted(FILES.items(), key=lambda (key, file_ob): key)
    for key, file_ob in file_list:
        if file_ob.size > FILE_MAXIMUM_SIZE:
            # TODO: 사용자에게 기각된 파일임을 알려야 한다
            continue
        file = server.file_manager.save_file(sess, int(article_id), file_ob.name)
        if not os.path.isdir('%s/%s' % (FILE_DIR, file.file_path)):
            os.makedirs('%s/%s' % (FILE_DIR, file.file_path))
        fp = open('%s/%s/%s' % (FILE_DIR, file.file_path, file.saved_filename), 'wb')
        fp.write(file_ob.read())

@warara.wrap_error
def write_(request, board_name):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    article_dic = {}
    r['url'] = ''.join(['/board/', board_name, '/'])
    article_dic['content'] = request.POST.get('text', '')
    use_signature = request.POST.get('signature_check', None)
    if use_signature:
        article_dic['content'] += '\n\n' + request.POST.get('signature', '')
    article_dic['title'] = request.POST.get('title', '')
    article_dic['heading'] = request.POST.get('heading', '') # Heading !!!
    if request.POST.get('write_type', 0) == 'modify':
        article_no = request.POST.get('article_no', 0)
        article_id = server.article_manager.modify_article(sess, board_name, int(article_no), WrittenArticle(**article_dic))

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
        _upload_file(server, sess, article_id, request.FILES)

    if request.POST.get('write_type', 0) == 'modify':
        return HttpResponseRedirect('/board/%s/%s#%s' % (board_name, request.POST.get('root_id', article_id), article_id))
    else:
        return HttpResponseRedirect('/board/%s/%s' % (board_name, str(article_id)))

def _read(request, r, sess, board_name, article_id):
    '''
    실제로 미들웨어에 접속하여 글을 읽어오는 함수.

    @type  request: Django Request
    @param request: Django Request
    @type  r: dictionary
    @param r: 렌더링에 사용될 dictionary
    @type  sess: string
    @param sess: LoginManager 에서 넘어온 세션
    @type  board_name: string
    @param board_name: 읽어올 글이 있는 게시판의 이름
    @type  article_id: string (int)
    @param article_id: 읽어올 글의 번호
    '''
    server = warara_middleware.get_server()
    article_list = server.article_manager.read_article(sess, board_name, int(article_id))
    username = request.session['arara_username']
    userid = request.session['arara_userid']

    for article in article_list:
        article.date = datetime.datetime.fromtimestamp(article.date)

        if article.deleted: #deleted article access
            article.author_nickname = ''
            article.author_username = ''
            article.content = '-- Deleted --'
            article.title  = '-- Deleted --'
            article.attach = None
            article.image = None
            continue

        if 'attach' in article.__dict__ and article.attach: #image view
            image_attach_list = []
            for file in article.attach:
                if file.filename.split('.')[-1].lower() in IMAGE_FILETYPE:
                    image_attach_list.append(file.file_id)
                    insert_image_tag = "<p><img src=\"/board/%s/%d/%d/file/%d/\"></img></p>" % (board_name, article.root_id, article.id, file.file_id)
                    image_attach_list.append(file.file_id)
            article.__dict__['image'] = image_attach_list

#        if article.depth > 12: #set depth 12 which has bigger depth than 12
#            article.depth = 12
#        article.depth_list = range(1, article.depth - 1)

        # Finally, render the content using content renderer
        article.content = render_content(article.content)

        if article.author_id == userid:
            article.flag_modify = 1
        else:
            article.flag_modify = 0

    r['board_name'] = board_name
    r['article_id'] = article_id
    r['user_signature'] = server.member_manager.get_info(sess).signature
    r['article_read_list'] = article_list
    r['root_article'] = article_list[0]
    # move_article 사용시 이동할 보드를 select 태그를 사용해 리스트로 불러와 쓰기 위함.
    board_list = server.board_manager.get_board_list()
    r['board_list'] = board_list
    # 2010.08.30. 시삽인지 아닌지를 캐싱하지 않기 때문에 아래 함수가 너무 빈번히 호출되고 있다.
    # 일단 현 단계에서는 사용하지 않도록 막음.
    # is_sysop_or_manager = server.member_manager.is_sysop(sess)
    # r['is_sysop_or_manager'] = is_sysop_or_manager
    r['is_sysop_or_manager'] = False # 캐싱이 도입되면 이 줄을 지우고 위 2줄로 되돌아가자.


@warara.wrap_error
def read(request, board_name, article_id):
    '''
    주어진 게시판의 주어진 글을 읽어온다.

    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: 읽고자 하는 글이 있는 Board Name
    @type  article_id: string (int)
    @param article_id: 읽고자 하는 글의 번호
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    r['mode'] = 'board'
    # 글의 정보를 r 에 저장
    _read(request, r, sess, board_name, article_id)

    # 화면 하단의 글목록의 정보를 r 에 저장
    get_article_list(request, r, 'read')

    # 계층형 Reply 구조를 위해 reply를 미리 render
    rendered_reply = render_reply(board_name, r['article_read_list'][1:], '/board/%s/' % board_name)
    r['rendered_reply'] = rendered_reply
    r['article'] = r['article_read_list'][0]

    rendered = render_to_string('board/read.html', r)

    return HttpResponse(rendered)

@warara.wrap_error
def read_root(request, board_name, article_id):
    '''
    주어진 게시판의 주어진 글이 답글인 경우 root글의 주소로 읽어온다.

    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: 읽고자 하는 글이 있는 Board Name
    @type  article_id: string (int)
    @param article_id: 읽고자 하는 글의 번호
    '''
    server = warara_middleware.get_server() #
    sess, r = warara.check_logged_in(request) #

    r['mode'] = 'board'
    article_list = server.article_manager.read_article(sess, board_name, int(article_id))

    root_article_id = article_list[0].root_id
    # 글의 정보를 r 에 저장
    _read(request, r, sess, board_name, root_article_id)

    # 화면 하단의 글목록의 정보를 r 에 저장
    get_article_list(request, r, 'read')

    rendered = render_to_string('board/read.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def _reply(request, board_name, article_id):
    '''
    주어진 게시판의 주어진 글에 실제로 reply 를 단다.

    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: reply를 달고자 하는 글이 있는 board name
    @type  article_id: string (int)
    @param article_id: reply를 달고자 하는 글의 번호
    @rtype: int
    @return: reply 가 달리는 글의 root id
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    reply_dic = {}
    reply_dic['content'] = request.POST.get('content', '')
    reply_dic['title'] = request.POST.get('title', '')
    reply_dic['heading'] = request.POST.get('heading', '') # TODO: HEADING !!
    root_id = request.POST.get('root_id', '')

    use_signature = request.POST.get('signature_check', None)
    if use_signature:
        reply_dic['content'] += '\n\n' + request.POST.get('signature', '')

    article_id = server.article_manager.write_reply(sess, board_name, int(article_id), WrittenArticle(**reply_dic))

    #upload file
    if request.FILES:
        _upload_file(server, sess, article_id, request.FILES)

    return root_id

@warara.wrap_error
def _relay_fiction_reply(request, board_name, article_id):
    '''
    이벤트용 임시 답글 함수.

    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: reply를 달고자 하는 글이 있는 board name
    @type  article_id: string (int)
    @param article_id: reply를 달고자 하는 글의 번호
    @rtype: int
    @return: reply 가 달리는 글의 root id
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    reply_dic = {}
    color = request.POST.get('color', '#000000')
    reply_dic['content'] = '<font color=\"' + color + '\">' + request.POST.get('content', '') + '</font>'
    reply_dic['title'] = request.POST.get('title', '')
    reply_dic['heading'] = request.POST.get('heading', '') # TODO: HEADING !!
    root_id = request.POST.get('root_id', '')

    use_signature = request.POST.get('signature_check', None)
    if use_signature:
        reply_dic['content'] += '\n\n' + request.POST.get('signature', '')

    article_id = server.article_manager.write_reply(sess, board_name, int(article_id), WrittenArticle(**reply_dic))

    return root_id

@warara.wrap_error
def reply(request, board_name, article_id):
    '''
    주어진 게시판의 주어진 글에 reply 를 단다.

    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: reply를 달고자 하는 글이 있는 board name
    @type  article_id: string (int)
    @param article_id: reply를 달고자 하는 글의 번호
    @rtype: HttpResponseRedirect
    @return: 답글이 달린 원글을 읽는 페이지로 재전송

    '''
    root_id = _reply(request, board_name, article_id)

    return HttpResponseRedirect('/board/%s/%s/' % (board_name, str(root_id)))

@warara.prevent_cached_by_browser
@warara.wrap_error
def vote(request, board_name, root_id, article_no, vote_type):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    if vote_type == '+':
        positive_vote = True
    else:
        positive_vote = False

    try:
        server.article_manager.vote_article(sess, board_name, int(article_no), positive_vote)
        response = HttpResponse("OK")
    except InvalidOperation, e:
        response = HttpResponse("ALREADY_VOTED")

    return response

@warara.wrap_error
def move_article(request):
    '''
    현재 글과 그 리플들을 다른 게시판으로 이동하며, article_vote_status, files의 보드 정보를 함께 수정한다.
    @type   request: Django Request
    @param  request: POST로 넘어온 form 정보.
    @rtype: HttpResponseRedirect
    @return: 현재 글이 이동되고 없는 보드의 목록 페이지로 재전송
    '''
    # TODO: 굳이 이게 POST 여야 할 필요가 있을까?
    # TODO: 권한이 있는 사용자의 행동인지 점검할 필요가 있다
    if request.method == 'POST':
        server = warara_middleware.get_server()
        sess, r = warara.check_logged_in(request)
        board_name = request.POST['board_name']
        article_no = request.POST['article_no']
        board_to_move = request.POST['board_to_move']
        server.article_manager.move_article(sess, board_name, int(article_no), board_to_move)
        return HttpResponseRedirect('/board/%s/' % board_name)

@warara.wrap_error
def _delete(request, board_name, root_id, article_no):
    '''
    주어진 게시판의 주어진 글을 실제로 지운다.

    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: 지우고자 하는 글이 있는 board name
    @type  root_id: string (int)
    @param root_id: 지우고자 하는 글이 달린 원글의 번호
    @type  article_id: string (int)
    @param article_id: 지우고자 하는 글의 번호
    '''
    # XXX 어째서 root_id 가 있어야 글을 지울 수 있는 걸까 ???
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    
    server.article_manager.delete_article(sess, board_name, int(article_no))

@warara.wrap_error
def delete(request, board_name, root_id, article_no):
    '''
    주어진 게시판의 주어진 글을 지운다.

    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: 지우고자 하는 글이 있는 board name
    @type  root_id: string (int)
    @param root_id: 지우고자 하는 글이 달린 원글의 번호
    @type  article_id: string (int)
    @param article_id: 지우고자 하는 글의 번호
    @rtype: HttpResponseRedirect
    @return: 삭제된 글이 달려 있던 루트 글로 이동

    '''
    _delete(request, board_name, root_id, article_no)

    return HttpResponseRedirect('/board/%s/%s/' % (board_name, root_id))

def destroy(request, board_name, root_id, article_no):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    server.article_manager.destroy_article(sess, board_name, int(article_no))
    # XXX 2010.05.14.
    # 글을 destroy하였으므로 해당 보드로 돌아간다.
    # 추후에는 pageno 정보를 이용하도록 수정하는 게 좋겠다.
    # 어차피 지금은 SYSOP 이 아니면 이 작업을 할 수 없지만.
    return HttpResponseRedirect('/board/%s/' % board_name)
    # XXX 여기까지.

def _search(request, r, sess, board_name):
    '''
    주어진 게시판에서 실제로 글을 검색한다.

    @type  request: Django Request
    @param request: Django Request
    @type  r: dictionary
    @param r: 렌더링에 사용될 dictionary
    @type  sess: string
    @param sess: LoginManager 에서 넘어온 세션
    @type  board_name: string
    @param board_name: 검색하려는 글이 있는 게시판의 이름
    '''
    
    if board_name != u'':
        r['board_name'] = board_name
    else:
        r['board_name'] = u'All Articles'

    r['selected_method_list'] = ['title', 'content', 'author_nickname', 'author_username']
    r['search_method_list'] = [{'val':'title', 'text':'제목'}, {'val':'content', 'text':'본문'},
            {'val':'author_nickname', 'text':'글쓴이'}, {'val':'author_username', 'text':'ID'}]
    search_word = request.GET.get('search_word', '')
    r['search_word'] = search_word
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
    if board_name != u'':
        get_article_list(request, r, 'search')
    else:
        get_article_list(request, r, 'total_search')

    r['method'] = 'search'
    # XXX 2010.05.14.
    #  바로 다음 줄의 request.get_full_path() 를 호출하면 이상하게도 utf-8 error 가 발생한다. 한글로 검색했을 때 주로 발생하는데, 문제의 재현이 쉽지 않다. 어떤 땐 utf-8 error 가 나고, 어떤 땐 안 난다.
    # XXX 여기까지.
    path = request.get_full_path()
    path = path.split('?')[0]
    r['path'] = path + "?search_word=" + search_word + "&chosen_search_method=" + r['chosen_search_method']

@warara.wrap_error
def search(request, board_name):
    '''
    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: 검색하려는 글이 있는 board name
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request);

    r['mode'] = 'board'
    _search(request, r, sess, board_name)

    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

# Django's never_cache decorator causes empty file, so we do it manually.
# NOTE: Django's cache warara_middleware uses cache backends with timeout value from http headers
#       with simultaneously setting appropriate http headers to control web browsers.
# reference: http://code.google.com/p/cciu-open-course-labs/source/browse/opencourselabs/utils/__init__.py
@warara.prevent_cached_by_browser
@warara.wrap_error
def file_download(request, board_name, article_root_id, article_id, file_id):
    server = warara_middleware.get_server()
    file = server.file_manager.download_file(int(article_id), int(file_id))
    file_path = "%s/%s/%s" % (FILE_DIR, file.file_path, file.saved_filename)
    file_ob = open(file_path, 'rb')
    response = HttpResponse(file_ob.read())
    file_ob.close()
    type, encoding = mimetypes.guess_type(file.real_filename)
    if type is None:
        type = 'application/octet-stream'
    response['Content-Type'] = type
    response['Content-Length'] = str(os.stat(file_path).st_size)
    if encoding is not None:
        response['Content-Encoding'] = encoding

    if u'WebKit' in request.META['HTTP_USER_AGENT']:
        filename_header = 'filename=%s' % file.real_filename.encode('utf-8')
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        filename_header = ''
    else:
        filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(file.real_filename.encode('utf-8'))

    response['Content-Disposition'] = 'attachment; ' + filename_header
    return response

@warara.wrap_error
def rss(request, board_name):
    '''
    주어진 게시판에 대한 RSS 파일을 제공한다.

    @type  request: Django Request
    @param request: Request
    @type  board_name: string
    @param board_name: 검색하려는 글이 있는 board name
    '''

    from django.utils import feedgenerator

    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    feed = feedgenerator.Atom1Feed(title = u'ARA/%s' % board_name, link = u'/board/%s/rss/' % board_name, description = u'A RSS of all articles in %s board' % board_name)
    
    page_no = 1
    page_length = 20
    article_list = server.article_manager.article_list(sess, board_name, None, page_no, page_length, True).hit

    for article in article_list:
        if article.heading:
            article_title = u'[%s] %s' % (article.heading, article.title)
        else:
            article_title = u'%s' % article.title
        feed.add_item(title=article_title,
            link=u'/board/%s/%d/' % (board_name, article.id),
            author_name=article.author_nickname,
            pubdate=datetime.datetime.fromtimestamp(article.date),
            description=u'author : %s date : %s' % (article.author_nickname, datetime.datetime.fromtimestamp(article.date)))

    return HttpResponse(feed.writeString('utf-8'), mimetype=feedgenerator.Atom1Feed.mime_type)

# Using Django's default HTML handling util, escape all tags and urlize, and do some content substitution.
# 동시에 <a> tag 를 target="_blank" 로 설정되도록 regex 를 써서 바꿔버린다.
# TODO: 더 나은 방법이 있다면 (CSS 에 a tag 에 속성 먹이기가 더 예쁘지 않을까...전체를 div class 로 감싸서)
#       그거로 바꾸기!
from django.utils import html
import re
youtube_tag = re.compile(r'http(?:s?)://(?:www\.)?youtu(?:be\.com/watch\?v=|\.be/)([\w\-]+)(&(amp;)?[\w\?=]*)?')
a_tag = re.compile(r'<a href="(.+?)">')
def render_content(content):
    content = html.escape(content)
    # Do the substitution
    content = youtube_tag.sub(r'\g<0>\n<iframe width="560" height="315" src="http://www.youtube.com/embed/\1" frameborder="0" allowfullscreen></iframe>\n', content)
    content = html.urlize(content)
    content = a_tag.sub(r'<a href="\1" target="_blank">', content)
    return content

def render_reply(board_name, article_list, base_url):
    if article_list == []:
        return ''

    r_string = ''
    target_depth = article_list[0].depth

    for i in xrange(len(article_list)):
        if article_list[i].depth == target_depth:
            target_article = article_list[i]
            target_children_list = []
        else:
            target_children_list.append(article_list[i])
        
        if i+1 == len(article_list) or article_list[i+1].depth == target_depth:
            rendered_target_children = render_reply(board_name, target_children_list, base_url)
            rendered_target_article = render_to_string('board/read_reply.html', {'article': target_article, 'rendered_reply': rendered_target_children, 'board_name': board_name, 'base_url': base_url})
            r_string += rendered_target_article

    return r_string
