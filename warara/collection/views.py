# -*- coding: utf-8 -*-
import datetime

from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from arara_thrift.ttypes import *
import warara
import warara.board.views
from warara import warara_middleware


COLLECTION_TYPE = {
        'all':
            {'board_name': u'All Articles',
             'rss_desc': u'RSS of all articles in ARA',
             'base_url': u'/all/',
             'list_mode': 'total_list',
             'read_mode': 'total_read'},
        'scrapbook':
            {'board_name': u'Scrapped Articles',
             'rss_desc': u'RSS of articles that you scrapped',
             'base_url': u'/scrapbook/',
             'list_mode': 'scrap_list',
             'read_mode': 'scrap_read'},
}
COLLECTION_LIST = COLLECTION_TYPE.keys()

def check_valid_collection(function):
    def wrap(request, *args, **kwargs):
        mode = kwargs.pop('mode', '')
        if mode not in COLLECTION_LIST:
            return HttpResponseRedirect('/')
        return function(request, mode, *args, **kwargs)
    return wrap

@check_valid_collection
@warara.wrap_error
def list(request, mode):
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    # board_name 이 없기 때문에 사용한 Hack.
    r['board_name'] = COLLECTION_TYPE[mode]['board_name']
    r['mode'] = mode

    warara.board.views.get_article_list(request, r, COLLECTION_TYPE[mode]['list_mode'])

    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

@check_valid_collection
@warara.wrap_error
def read(request, mode, article_id):
    '''
    컬렉션의 주어진 글을 읽어온다.

    @type  request: Django Request
    @param request: Request
    @type  article_id: string (int)
    @param article_id: 읽고자 하는 글의 번호
    '''
    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    # 글의 정보를 r 에 저장
    warara.board.views._read(request, r, sess, u'', article_id)

    # 화면 하단의 글목록의 정보를 r 에 저장
    warara.board.views.get_article_list(request, r, COLLECTION_TYPE[mode]['read_mode'])

    # board_name 이 없기 때문에 사용한 Hack.
    r['board_name'] = COLLECTION_TYPE[mode]['board_name']
    r['mode'] = mode

    # 계층형 Reply 구조를 위해 reply를 미리 render
    r['rendered_reply'] = warara.board.views.render_reply(r['board_name'], r['article_read_list'][1:], COLLECTION_TYPE[mode]['base_url'])
    r['article'] = r['article_read_list'][0]

    rendered = render_to_string('board/read.html', r)
    return HttpResponse(rendered)

@check_valid_collection
@warara.wrap_error
def reply(request, mode, article_id):
    '''
    컬렉션의 주어진 글에 reply 를 단다.

    @type  request: Django Request
    @param request: Request
    @type  article_id: string (int)
    @param article_id: reply를 달고자 하는 글의 번호
    @rtype: HttpResponseRedirect
    @return: 답글이 달린 원글을 읽는 페이지로 재전송

    '''
    root_id = warara.board.views._reply(request, u'', article_id)

    return HttpResponseRedirect(COLLECTION_TYPE[mode]['base_url'] + str(root_id) + '/')

@check_valid_collection
@warara.wrap_error
def vote(request, root_id, article_no):
    return warara.board.views.vote(request, u'', root_id, article_no)

@check_valid_collection
@warara.wrap_error
def delete(request, mode, root_id, article_no):
    '''
    컬렉션에서 주어진 글을 지운다.

    @type  request: Django Request
    @param request: Request
    @type  root_id: string (int)
    @param root_id: 지우고자 하는 글이 달린 원글의 번호
    @type  article_id: string (int)
    @param article_id: 지우고자 하는 글의 번호
    @rtype: HttpResponseRedirect
    @return: 삭제된 글이 달려 있던 루트 글로 이동

    '''
    warara.board.views._delete(request, u'', root_id, article_no)

    return HttpResponseRedirect(COLLECTION_TYPE['mode']['base_url'] + str(root_id) + '/')

@check_valid_collection
@warara.wrap_error
def search(request, mode):
    '''
    모든 게시판을 대상으로 검색.

    @type  request: Django Request
    @param request: Request
    '''
    if mode not in COLLECTION_LIST:
        return HttpResponseRedirect('/')

    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request);
    r['mode'] = mode

    if mode == 'all':
        warara.board.views._search(request, r, sess, u'')
    elif mode == 'scrap':
        return HttpResponse('Not Supported yet.')

    rendered = render_to_string('board/list.html', r)
    return HttpResponse(rendered)

@check_valid_collection
@warara.wrap_error
def rss(request, mode):
    '''
    컬렉션에 대한 RSS 파일을 제공한다.

    @type  request: Django Request
    @param request: Request
    '''

    from django.utils import feedgenerator

    server = warara_middleware.get_server()
    sess, r = warara.check_logged_in(request)

    feed = feedgenerator.Atom1Feed(title = u'ARA', link = COLLECTION_TYPE[mode]['base_url'] + 'rss/', description = COLLECTION_TYPE[mode]['rss_desc'])

    page_no = 1
    page_length = 20

    if mode == 'all':
        article_list = server.article_manager.article_list(sess, u"", u"", page_no, page_length, True).hit
    elif mode == 'scrap':
        article_list = server.article_manager.scrapped_article_list(sess, page_no, page_length).hit

    for article in article_list:
        feed.add_item(title='[%s]%s' % (article.board_name, article.title),
            link = COLLECTION_TYPE[mode]['base_url'] + '%d/' % article.id,
            author_name=article.author_nickname,
            pubdate=datetime.datetime.fromtimestamp(article.date),
            description=u'author : %s date : %s' % (article.author_nickname, datetime.datetime.fromtimestamp(article.date)))

    return HttpResponse(feed.writeString('utf-8'), mimetype=feedgenerator.Atom1Feed.mime_type)

@check_valid_collection
@warara.wrap_error
def file_download(request, mode, article_root_id, article_id, file_id):
    return warara.board.views.file_download(request, u'', article_root_id, article_id, file_id)
