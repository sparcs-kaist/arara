# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.cache import cache

from arara_thrift.ttypes import *
from urlparse import urlparse

import os
import datetime
import re
import warara
from warara import warara_middleware
from warara.board.views import fake_author

from etc.warara_settings import FILE_DIR, FILE_MAXIMUM_SIZE

IMAGE_FILETYPE = ['jpg', 'jpeg', 'gif', 'png']
IS_ARTICLE_LIST_PAGE = re.compile(r'^/mobile/all/$')

import warara.mobile.board.views

@warara.prevent_cached_by_browser
@warara.wrap_error_mobile
def list(request):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    # board_name 이 없기 때문에 사용한 Hack.
    r['board_name'] = u'All Articles'
    r['mode'] = 'all'
    warara.mobile.board.views.get_article_list(request, r, 'total_list')
    fake_author(r['article_list'], False)

    rendered = render_to_string('mobile/board/list.html', r)
    return HttpResponse(rendered)

@warara.prevent_cached_by_browser
@warara.wrap_error_mobile
def read(request, article_id):
    '''
    모든 게시판의 주어진 글을 읽어온다.

    @type  request: Django Request
    @param request: Request
    @type  article_id: string (int)
    @param article_id: 읽고자 하는 글의 번호
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)
    
    # 글의 정보를 r 에 저장
    warara.mobile.board.views._read(request, r, sess, u'', article_id)

    # 화면 하단의 글목록의 정보를 r 에 저장
    warara.mobile.board.views.get_article_list(request, r, 'total_read')

    # board_name 이 없기 때문에 사용한 Hack.
    r['board_name'] = u'All Articles'
    r['mode'] = 'all'

    fake_author(r['article_read_list'])
    fake_author(r['article_list'], False)

    # 계층형 Reply 구조를 위해 reply를 미리 render
    rendered_reply = warara.mobile.board.views.render_reply(u'All Articles', r['article_read_list'][1:], '/all/', 'all')
    r['rendered_reply'] = rendered_reply
    r['article'] = r['article_read_list'][0]

    # 만약 REFERER가 All의 LIST이면 backlink를 해당 페이지로 설정.
    # 그렇지 않으면 All의 첫 페이지로 설정
    referer = request.META.get('HTTP_REFERER') or '/'
    prev_path = urlparse(referer)

    if IS_ARTICLE_LIST_PAGE.match(prev_path.path) is not None:
        r['backlink'] = prev_path.path + '?' + prev_path.query
    else:
        r['backlink'] = '/mobile/all/'

    rendered = render_to_string('mobile/board/read.html', r)
    return HttpResponse(rendered)

@warara.wrap_error_mobile
def reply(request, article_id):
    '''
    모든 게시판의 주어진 글에 reply 를 단다.

    @type  request: Django Request
    @param request: Request
    @type  article_id: string (int)
    @param article_id: reply를 달고자 하는 글의 번호
    @rtype: HttpResponseRedirect
    @return: 답글이 달린 원글을 읽는 페이지로 재전송

    '''
    root_id, new_article_id = warara.mobile.board.views._reply(request, u'', article_id)

    return HttpResponseRedirect('/mobile/all/%s/#%d' % (str(root_id), new_article_id))

@warara.wrap_error_mobile
def vote(request, root_id, article_no):
    return warara.mobile.board.views.vote(request, u'', root_id, article_no)

@warara.wrap_error_mobile
def delete(request, root_id, article_no):
    '''
    모든 게시판의 주어진 글을 지운다.

    @type  request: Django Request
    @param request: Request
    @type  root_id: string (int)
    @param root_id: 지우고자 하는 글이 달린 원글의 번호
    @type  article_id: string (int)
    @param article_id: 지우고자 하는 글의 번호
    @rtype: HttpResponseRedirect
    @return: 삭제된 글이 달려 있던 루트 글로 이동

    '''
    warara.mobile.board.views._delete(request, u'', root_id, article_no)

    return HttpResponseRedirect('/mobile/all/%s/' % root_id)

@warara.wrap_error_mobile
def search(request):
    '''
    모든 게시판을 대상으로 검색.

    @type  request: Django Request
    @param request: Request
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request);
    r['mode'] = 'all'

    warara.mobile.board.views._search(request, r, sess, u'')

    rendered = render_to_string('mobile/board/list.html', r)
    return HttpResponse(rendered)

@warara.prevent_cached_by_browser
@warara.wrap_error_mobile
def file_download(request, article_root_id, article_id, file_id):
    return warara.mobile.board.views.file_download(request, u'', article_root_id, article_id, file_id)
