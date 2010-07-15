# -*- coding: utf-8 -*-
import datetime
import time
import logging

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import eagerload
from arara import model
from arara.util import require_login, filter_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import datetime2timestamp
from arara.util import smart_unicode

from arara_thrift.ttypes import *

log_method_call = log_method_call_with_source('article_manager')
log_method_call_important = log_method_call_with_source_important('article_manager')

# TODO: WRITE_ARTICLE_DICT 는 사실 쓰이지 않는다... SPEC 표시 용도일까?
WRITE_ARTICLE_DICT = ('title', 'heading', 'content')
READ_ARTICLE_WHITELIST = ('id', 'heading', 'title', 'content', 'last_modified_date', 'deleted', 'blacklisted', 'author_username', 'author_nickname', 'author_id', 'vote', 'date', 'hit', 'depth', 'root_id', 'is_searchable', 'attach', 'board_name')
LIST_ARTICLE_WHITELIST = ('id', 'title', 'heading', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'author_id', 'vote', 'hit', 'board_name')
# TODO SEARCH_ARTICLE_WHITELIST 는 왜 여기에도 있는 걸까?
SEARCH_ARTICLE_WHITELIST = ('id', 'title', 'heading', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'author_id', 'vote', 'hit', 'content')
BEST_ARTICLE_WHITELIST = ('id', 'title', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'author_id', 'vote', 'hit', 'last_page', 'board_name')

LIST_ORDER_ROOT_ID         = 0
LIST_ORDER_LAST_REPLY_DATE = 1

class ArticleManager(object):
    '''
    게시글 및 검색 처리 클래스
    현재 게시글 표시방식이 절묘하기 때문에 read 메소드에 관한 논의가 필요.
    '''
    def __init__(self, engine):
        self.logger = logging.getLogger('article_manager')
        self.engine = engine

    def _article_thread_to_list(self, article_thread, session_key, blacklisted_userid):
        # 기존에 반복문 2개로 하던 걸 1개로 줄여봄.
        stack = []
        ret = []
        article_id_list = []
        stack.append((article_thread, 1))
        while stack:
            art, dep = stack.pop()
            for child in art.children[::-1]:
                stack.append((child, dep + 1))
            dic = self._get_dict(art, READ_ARTICLE_WHITELIST)
            dic['depth'] = dep

            if dic['author_id'] in blacklisted_userid:
                dic['blacklisted'] = True
            else:
                dic['blacklisted'] = False

            article_id_list.append(dic['id'])
            dic['date'] = datetime2timestamp(dic['date'])
            dic['last_modified_date'] = datetime2timestamp(dic['last_modified_date'])
            ret.append(Article(**dic))

        self.engine.read_status_manager.mark_as_read_list(session_key, article_id_list)
        return ret

    def _get_best_article(self, session_key, board_id, count, time_to_filter, best_type):
        session = model.Session()
        time_to_filter = datetime.datetime.fromtimestamp(time.time()-time_to_filter)
        if board_id:
            query = session.query(model.Article, model.Board).filter(and_(
                    model.articles_table.c.board_id==board_id,
                    model.articles_table.c.board_id==model.board_table.c.id,
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > time_to_filter,
                    not_(model.board_table.c.hide==True),
                    not_(model.board_table.c.deleted==True),
                    not_(model.articles_table.c.deleted==True)))
        else:
            query = session.query(model.Article, model.Board).filter(and_(
                    model.articles_table.c.board_id==model.board_table.c.id,
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > time_to_filter,
                    not_(model.board_table.c.hide==True),
                    not_(model.board_table.c.deleted==True),
                    not_(model.articles_table.c.deleted==True)))

        joined_best_article = query.order_by(model.Article.vote.desc()).order_by(model.Article.reply_count.desc()).order_by(model.Article.id.desc())[:count]
        best_article = [article for article, _ in joined_best_article]
        best_article_dict_list = self._get_dict_list(best_article, BEST_ARTICLE_WHITELIST)
        session.close()

        best_article_list = list()
        for article in best_article_dict_list:
            article['type'] = best_type
            article['date'] = datetime2timestamp(article['date'])
            article['last_modified_date'] = datetime2timestamp(article['last_modified_date'])
            best_article_list.append(Article(**article))
        return best_article_list

    def _get_dict(self, item, whitelist=None):
        session = model.Session()
        item_dict = item.__dict__
        if not item_dict.get('title'):
            item_dict['title'] = u'Untitled'
        if item_dict.has_key('author_id'):
            item_dict['author_username'] = item.author.username
            item_dict['author_nickname'] = item.author.nickname
        if item_dict.has_key('board_id'):
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
        if item_dict.has_key('heading_id'):
            if item.heading == None:
                item_dict['heading'] = u''
            else:
                item_dict['heading'] = item.heading.heading
        if not item_dict.get('root_id'):
            item_dict['root_id'] = item_dict['id']
        if item_dict.has_key('content'):
            if whitelist == SEARCH_ARTICLE_WHITELIST:
                item_dict['content'] = item_dict['content'][:40]
            if whitelist == READ_ARTICLE_WHITELIST:
                attach_files = session.query(model.File).filter_by(
                        article_id=item.id).filter_by(deleted=False)
                if attach_files.count() > 0:
                    item_dict['attach'] = [AttachDict(filename=x.filename, file_id=x.id) for x in attach_files]
        session.close()

        if whitelist:
            return filter_dict(item_dict, whitelist)
        else:
            return item_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        for item in raw_list:
            yield self._get_dict(item, whitelist)

    def _get_user(self, session, session_key):
        user_id = self.engine.login_manager.get_user_id(session_key)
        try:
            user = session.query(model.User).filter_by(id=user_id).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('user does not exist')
        return user

    def _get_user_id(self, session_key):
        return self.engine.login_manager.get_user_id(session_key)

    def _get_article(self, session, board_id, article_id):
        '''
        Internal Function.
        SQLAlchemy 세션을 이용하여 게시판의 글을 하나 읽어온다.

        @type  session: SQLAlchemy session
        @param session: 현재 사용중인 SQLAlchemy session
        @type  board_id: int
        @param board_id: 읽고자 하는 글이 있는 게시판의 id (단, None 일 때는 모든 게시판이라 가정)
        @type  article_id: int
        @param article_id: 읽고자 하는 글의 id
        @rtype: model.Article
        @return: DB 에서 읽어들인 SQLAlchemy Article 객체
        '''
        try:
            if board_id:
                article = session.query(model.Article).filter_by(board_id=board_id, id=article_id).one()
            else:
                article = session.query(model.Article).filter_by(id = article_id).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation("article does not exist")
        return article

    def _get_last_page(self, article_count, page_length):
        last_page = int(article_count / page_length)
        if article_count % page_length != 0:
            last_page += 1
        elif article_count == 0:
            last_page += 1
        return last_page

    @log_method_call
    def get_today_best_list(self, count=5):
        '''
        전체 보드에서 투베를 가져오는 함수

        @type  count: integer
        @param count: Number of today's best articles to get
        @rtype: list
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. 데이터베이스 오류: InternalError Exception 
        '''
        return self._get_best_article(None, None, count, 86400, 'today')

    @log_method_call
    def get_today_best_list_specific(self, board_name, count=5):
        '''
        해당 보드에서 투베를 가져오는 함수

        @type  board_name: string
        @param board_name: Board Name
        @type  count: integer
        @param count: Number of today's best articles to get
        @rtype: list
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        board_id = self.board_manager.get_board_id(board_name)
        return self._get_best_article(None, board_id, count, 86400, 'today')

    @log_method_call
    def get_weekly_best_list(self, count=5):
        '''
        전체 보드에서 윅베를 가져오는 함수

        @type  board_name: string
        @param board_name: Board Name
        @type  count: integer
        @param count: Number of today's best articles to get
        @rtype: list
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        return self._get_best_article(None, None, count, 604800, 'weekly')

    @log_method_call
    def get_weekly_best_list_specific(self, board_name, count=5):
        '''
        해당 보드에서 윅베를 가져오는 함수

        @type  board_name: string
        @param board_name: Board Name
        @type  count: integer
        @param count: Number of today's best articles to get
        @rtype: list
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception 
                2. 데이터베이스 오류: InternalError Exception
        '''
        board_id = self.engine.board_manager.get_board_id(board_name)
        return self._get_best_article(None, board_id, count, 604800, 'weekly')

    @log_method_call
    @require_login
    def not_read_article_list(self, session_key, page=1, page_length=20):
        '''
        사용자가 안 읽은 글들의 no을 리던해주는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, list
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: Not Read Article List
            2. 리스트 읽어오기 실패:
                1. 페이지 번호 오류: InvalidOperation Exception 
                2. 데이터베이스 오류: InternalError Exception
        '''

        try:
            session = model.Session()
            offset = page_length * (page - 1)
            last = offset + page_length
            # XXX: 갖고 와서 빼는군여. 가져올 때 빼세요.
            article_list = session.query(model.Article).filter_by(root_id=None).order_by(model.Article.id.desc())[offset:last]
            article_dict_list = self._get_dict_list(article_list, LIST_ARTICLE_WHITELIST)
            article_number = []
            for article in article_dict_list:
                article_number.append(article['id'])
            read_stats_list = self.engine.read_status_manager.check_stats(session_key, article_number)
            #not_read_article = filter(lambda x : x = 'N', read_stats_list) 
            not_read_article_number = []
            for i in range(len(read_stats_list)):
                if read_stats_list[i] == 'N':
                    not_read_article_number.append(article_number[i])
            article_count = len(not_read_article_number) 
            last_page = self._get_last_page(article_count, page_length)
            if page > last_page:
                session.close()
                raise InvalidOperation('WRONG_PAGENUM')

            session.close()
            ret = ArticleNumberList()
            ret.hit = not_read_article_number
            ret.last_page = last_page
            ret.results = article_count
            return ret
        except InvalidRequestError:
            session.close()
            raise InternalError('DATABASE_ERROR')


    @log_method_call
    @require_login
    def new_article_list(self, session_key, page=1, page_length=20):
        '''
        제대로 작동하지 않는 함수. 다시 코딩하여야 함.
        사용자가 로그아웃한 이후 게시판에 새로 올라온 글 또는 수정된 글들을 불러오는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, list
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: New Article List
            2. 리스트 읽어오기 실패:
                1. 페이지 번호 오류: InvalidOperation Exception 
                2. 데이터베이스 오류: InternalError Exception
        '''

        try:
            session = model.Session()
            user = self._get_user(session, session_key)
            article_count = article_list = session.query(model.Article).filter(and_(
                                model.articles_table.c.root_id==None,
                                model.articles_table.c.last_modified_date > user.last_logout_time)).count()
            last_page = self._get_last_page(article_count, page_length)
            if page > last_page:
                session.close()
                raise InvalidOperation('WRONG_PAGENUM')
            offset = page_length * (page - 1)
            last = offset + page_length

            article_list = session.query(model.Article).filter(and_(
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > user.last_logout_time)).order_by(model.Article.id.desc())[offset:last]
            article_dict_list = self._get_dict_list(article_list, LIST_ARTICLE_WHITELIST)
            session.close()

            ret = ArticleList()
            ret.hit = list()
            for article in article_dict_list:
                article['read_status'] = 'N'
                article['date'] = datetime2timestamp(article['date'])
                article['last_modified_date'] = datetime2timestamp(article['last_modified_date'])
                ret.hit.append(Article(**d))
            ret.last_page = last_page
            ret.results = article_count
            return ret
        except InvalidRequestError:
            session.close()
            raise InternalError('DATABASE_ERROR')


    def _get_blacklist_userid(self, session_key):
        try:
            blacklist_list = self.engine.blacklist_manager.get_article_blacklisted_userid_list(session_key)
        except NotLoggedIn:
            blacklist_list = []
            pass
        return set(blacklist_list)

    def _get_article_list(self, board_name, heading_name, page, page_length, include_all_headings = True, order_by = LIST_ORDER_ROOT_ID):
        '''
        Internal.
        주어진 게시판의 주어진 페이지에 있는 글의 목록을 가져온다.

        @type  board_name: string
        @param board_name: 글을 가져올 게시판의 이름
        @type  heading_name: string
        @param heading_name: 가져올 글의 글머리 이름
        @type  page: int
        @param page: 글을 가져올 페이지의 번호
        @type  page_length: int
        @param page_length: 페이지당 글 갯수
        @type  include_all_headings: boolean
        @param include_all_headings: 모든 글머리의 글을 가져올지에 대한 여부
        @type  order_by: int - LIST_ORDER
        @param order_by: 글 정렬 방식 (현재는 LIST_ORDER_ROOT_ID 만 테스트됨)
        @rtype: (list<article_dict>, int, int, list<int>)
        @return:
            1. article_dict_list : article_dict 의 list
            2. last page         : 글 목록의 마지막 페이지의 번호
            3. article_count     : 글의 전체 갯수
            4. article_last_reply_id_list : 글 목록의 각 글에 달린 마지막 reply 의 번호목록
        '''
        session = model.Session()
        desired_query = session.query(model.Article)

        if board_name != u'':
            # 해당 board 에 있는 글만 선택한다
            board_id = self.engine.board_manager.get_board_id(board_name)
            desired_query = desired_query.filter_by(board_id=board_id, root_id=None, destroyed=False)

            if not include_all_headings:
                # 특정 말머리만 선택한다
                heading = self.engine.board_manager._get_heading_by_boardid(session, board_id, heading_name)
                desired_query = desired_query.filter_by(heading=heading)
        else:
            # 모든 board 에 있는 글을 선택한다.
            desired_query = desired_query.filter_by(root_id=None, destroyed=False)

        article_count = desired_query.count()
        last_page = self._get_last_page(article_count, page_length)
        # Page 에 0 이 들어오면 계속 잘못 작동하고 있다. 이를 막기 위해 page 의 시작점을 0 으로 설정한다.
        # XXX 가능하면 TEST CODE 도 만들자.
        if page == 0:
            page = 1
        # 페이지가 넘치면? InvalidOperation.
        if page > last_page:
            session.close()
            raise InvalidOperation('WRONG_PAGENUM')
        # Page 의 시작 글과 끝 글의 번째수를 구하고 Query 를 날린다.
        offset = page_length * (page - 1)
        last = offset + page_length

        # 목록의 정렬. 근데 조금 비효율적인 것 같기도 하고 ...
        article_list = None
        if order_by == LIST_ORDER_ROOT_ID:
            article_list = list(desired_query.order_by(model.Article.id.desc())[offset:last])
        elif order_by == LIST_ORDER_LAST_REPLY_DATE:
            article_list = list(desired_query.order_by(model.Article.last_reply_date.desc())[offset:last])
        else:
            article_list = list(desired_query.order_by(model.Article.id.desc())[offset:last])

        session.close()
        # 적당히 리턴한다.
        article_dict_list = self._get_dict_list(article_list, LIST_ARTICLE_WHITELIST)
        article_last_reply_id_list = [article.last_reply_id for article in article_list]
        return article_dict_list, last_page, article_count, article_last_reply_id_list

    def _article_list(self, session_key, board_name, heading_name, page, page_length, include_all_headings = True, order_by = LIST_ORDER_ROOT_ID):
        '''
        Internal.
        주어진 게시판의 주어진 페이지에 있는 글의 목록을 가져와 Thrift 형식의 Article 객체의 list 로 돌려준다.

        @type  session_key: string
        @param session_key: 사용자의 session_key
        @type  board_name: string
        @param board_name: 글을 가져올 게시판의 이름
        @type  heading_name: string
        @param heading_name: 가져올 글의 글머리 이름
        @type  page: int
        @param page: 글을 가져올 페이지의 번호
        @type  page_length: int
        @param page_length: 페이지당 글 갯수
        @type  include_all_headings: boolean
        @param include_all_headings: 모든 글머리의 글을 가져올지에 대한 여부
        @type  order_by: int - LIST_ORDER
        @param order_by: 글 정렬 방식 (현재는 LIST_ORDER_ROOT_ID 만 테스트됨)
        @rtype: list<Article>
        @return:
            선택한 게시판의 선택한 page 에 있는 글 (Article 객체) 의 list
        '''
        blacklisted_users = self._get_blacklist_userid(session_key)

        article_dict_list, last_page, article_count, article_last_reply_id_list = self._get_article_list(board_name, heading_name, page, page_length, include_all_headings, order_by)
        # InvalidOperation(board not exist) 는 여기서 알아서 불릴 것이므로 제거.

        # article_dict_list 를 generator 에서 list화.
        # 어차피 이 함수가 끝날때까지 append 되는 새 list 를 return 하므로 상관없다.
        article_dict_list = [x for x in article_dict_list]
        article_id_list = [article['id'] for article in article_dict_list]
        read_stats_list = None # Namespace 에 등록. Assign 은 요 바로 다음에서.

        try:
            read_stats_list = self.engine.read_status_manager.check_stats(session_key, article_id_list)
            read_stats_list_sub = self.engine.read_status_manager.check_stats(session_key, article_last_reply_id_list)
            for idx, item in enumerate(read_stats_list_sub):
                if read_stats_list[idx] == 'R':
                    if item == 'N':
                        read_stats_list[idx] = 'U'

        except NotLoggedIn, InvalidOperation:
            read_stats_list = ['N'] * len(article_id_list)

        # 이상의 내용을 바탕으로 article_list 를 채운다.
        article_list = ArticleList()
        article_list.hit = [None] * len(article_id_list)

        for idx, article in enumerate(article_dict_list):
            if article['author_id'] in blacklisted_users:
                article['blacklisted'] = True
            else:
                article['blacklisted'] = False
            if not article.has_key('type'):
                article['type'] = 'normal'

            article['read_status'] = read_stats_list[idx]

            article['date'] = datetime2timestamp(article['date'])
            article['last_modified_date'] = datetime2timestamp(article['last_modified_date'])
            article_list.hit[idx] = Article(**article)

        article_list.last_page = last_page
        article_list.results = article_count
        return article_list
         
    @log_method_call
    def article_list(self, session_key, board_name, heading_name, page=1, page_length=20, include_all_headings=True):
        '''
        게시판의 게시글 목록 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name : BBS Name (0글자 문자열을 넘기면 모든 게시판에 대하여 적용)
        @type  heading_name: string
        @param heading_name: 가져올 글의 글머리 이름
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @type  include_all_headings: boolean
        @param include_all_headings: 모든 글머리의 글을 가져올지에 대한 여부
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: Article List
            2. 리스트 읽어오기 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 페이지 번호 오류: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception 
        '''
        return self._article_list(session_key, board_name, heading_name, page, page_length, include_all_headings, LIST_ORDER_ROOT_ID)

    @require_login
    @log_method_call_important
    def read_article(self, session_key, board_name, no):
        '''
        DB로부터 게시글 하나를 읽어옴

        Article Dictionary { no, read_status, title, content, author, date, hit, vote }

        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type board_name: string
        @param board_name : BBS Name
        @rtype: dictionary
        @return:
            1. Read 성공: Article Dictionary
            2. Read 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception 
        '''

        session = model.Session()
        # XXX 주어진 boar_name 에 맞는지 check
        blacklisted_userid = self._get_blacklist_userid(session_key)

        try:
            article = session.query(model.Article).options(eagerload('children')).filter_by(id=no).one()
            msg = self.engine.read_status_manager.check_stat(session_key, no)
            if msg == 'N':
                article.hit += 1
                session.commit()
        except InvalidRequestError:
            session.rollback()
            session.close()
            raise InvalidOperation('ARTICLE_NOT_EXIST')
        article_dict_list = self._article_thread_to_list(article, session_key, blacklisted_userid)
        session.close()
        return article_dict_list

    def read_recent_article(self, session_key, board_name):
        '''
        DB로부터 가장 최근의 게시글 하나만을 읽어옴

        Article Dictionary { no, read_status, title, content, author, date, hit, vote }

        @type  session_key: string
        @param session_key: User Key
        @type board_name: string
        @param board_name : BBS Name
        @rtype: dictionary
        @return:
            1. Read 성공: Article Dictionary
            2. Read 실패:
                1. 최근 게시물이 존재하지 않음: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception 
        '''
        
        board_id = self.engine.board_manager.get_board_id(board_name)
        session = model.Session()
        blacklisted_userid = self._get_blacklist_userid(session_key)

        try:
            article = session.query(model.Article).options(eagerload('children')).filter_by(board_id=board_id).order_by(model.Article.id.desc()).first()
            if article == None:
                raise InvalidOperation('ARTICLE_NOT_EXIST')
            msg = self.engine.read_status_manager.check_stat(session_key, article.id)
            if msg == 'N':
                article.hit += 1
                session.commit()
        except InvalidRequestError:
            session.rollback()
            session.close()
            raise InvalidOperation('ARTICLE_NOT_EXIST')

        article_dict_list = self._article_thread_to_list(article, session_key, blacklisted_userid)
        session.close()
        return article_dict_list

    def _get_total_article_count(self, session, board_id, heading_id, include_all_headings = True):
        '''
        Internal.
        주어진 게시판에 있는 선택된 말머리에 해당되는 모든 글의 갯수를 센다.

        @type  session: SQLAlchemy Session
        @param session: 사용중인 session
        @type  board_name: int
        @param board_name: 글 갯수를 가져올 게시판의 id
        @type  heading_id: int
        @param heading_id: 글 갯수를 가져올 말머리의 id (없을 경우 None)
        @type  include_all_headings: bool
        @param include_all_headings: 모든 말머리를 가져올 것인지의 여부
        @rtype: int
        @return: 해당 게시판의 해당되는 말머리의 모든 글의 갯수
        '''
        query = session.query(model.Article)

        if board_id == None:
            query = query.filter_by(root_id=None, destroyed=False)
        else:
            query = query.filter_by(board_id=board_id, root_id=None, destroyed=False)
            if not include_all_headings:
                query = query.filter_by(heading_id=heading_id)

        return query.count()


    def _get_remaining_article_count(self, session, board_id, heading_id, no, include_all_headings = True, order_by = LIST_ORDER_ROOT_ID):
        '''
        Internal.
        주어진 게시판에 있는 선택된 말머리에 해당되는 글들 중 no 번 글 이후로 몇 개의 글이 있는지 센다.

        @type  session: SQLAlchemy Session
        @param session: 사용중인 session
        @type  board_id: int
        @param board_id: 글을 가져올 게시판의 id
        @type  heading_id: int
        @param heading_id: 목록에서 보여줄 선택된 말머리
        @type  no: int
        @param no: 글번호
        @type  include_all_headings: boolean
        @param include_all_headings: 모든 말머리를 보여줄 것인지의 여부
        @type  order_by: int - LIST_ORDER
        @param order_by: 글 정렬 방식 (현재는 LIST_ORDER_ROOT_ID 만 테스트됨)
        @rtype: int
        @return: 해당 게시판의 해당되는 말머리에서 no 번 이후 글의 개수 
        '''
        query = session.query(model.Article)

        if board_id == None:
            query = query.filter(and_(
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.destroyed==False,
                    model.articles_table.c.id < no))
        else:
            query = query.filter(and_(
                    model.articles_table.c.board_id==board_id,
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.destroyed==False,
                    model.articles_table.c.id < no))
            if not include_all_headings:
                query = query.filter_by(heading_id=heading_id)

        return query.count()

    def _article_list_below(self, session_key, board_name, heading_name, no, page_length, include_all_headings = True, order_by = LIST_ORDER_ROOT_ID):
        '''
        Internal.
        주어진 게시판의 주어진 게시물의 하단에 표시될 글의 목록을 가져와 Thrift 형식의 Article 객체의 list 로 돌려준다.

        @type  session_key: string
        @param session_key: 사용자의 session_key
        @type  board_name: string
        @param board_name: 글을 가져올 게시판의 이름
        @type  heading_name: string
        @param heading_name: 목록에서 보여줄 선택된 말머리
        @type  no: int
        @param no: 글번호
        @type  page_length: int
        @param page_length: 페이지당 글 갯수
        @type  include_all_headings: boolean
        @param include_all_headings: 모든 말머리를 보여줄 것인지의 여부
        @type  order_by: int - LIST_ORDER
        @param order_by: 글 정렬 방식 (현재는 LIST_ORDER_ROOT_ID 만 테스트됨)
        @rtype: list<Article>
        @return:
            선택한 게시판의 선택한 page 에 있는 글 (Article 객체) 의 list
        '''
        # TODO : session 을 굳이 따로 사용할 필요가 있나?
        session = model.Session()

        # Heading ID, Board ID 를 구한다
        board_id = None
        if board_name != u"":
            board_id = self.engine.board_manager.get_board_id(board_name)

        heading_id = None
        if not include_all_headings and heading_name != u"":
            heading_id = self.engine.board_manager._get_heading_by_boardid(session, board_id, heading_name).id

        # 게시판의 모든 글의 갯수를 확보한다.
        total_article_count = self._get_total_article_count(session, board_id, heading_id, include_all_headings)

        # 게시판에 선택된 글 이후의 글의 갯수를 센다
        remaining_article_count = self._get_remaining_article_count(session, board_id, heading_id, no, include_all_headings, order_by)

        session.close()
        # 이로부터 합당한 쪽번호를 계산한다
        position_no = total_article_count - remaining_article_count
        page_position = position_no / page_length
        if position_no % page_length != 0:
            page_position += 1

        # 이상을 바탕으로 _article_list 함수를 호출한다
        try:
            below_article_dict_list = self._article_list(session_key, board_name, heading_name, page_position, page_length, include_all_headings, order_by)
        except Exception:
            raise

        ret = ArticleList()
        ret.hit = below_article_dict_list.hit
        ret.current_page = page_position
        ret.last_page = below_article_dict_list.last_page
        ret.results = below_article_dict_list.results
        return ret
 

    @require_login
    @log_method_call
    def article_list_below(self, session_key, board_name, heading_name, no, page_length=20, include_all_headings=True):
        '''
        게시물을 읽을 때 밑에 표시될 게시글 목록을 가져오는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @type  heading_name: string
        @param heading_name: 가져올 글의 글머리 이름
        @type  no: integer
        @param no: Article No
        @type  page_length: integer
        @param page_length: Number of articles to be displayed on a page
        @type  include_all_headings: boolean
        @param include_all_headings: 모든 글머리의 글을 가져올지에 대한 여부
        @rtype: Article List
        @return:
            1. 목록 가져오기 성공: Article List
            2. 목록 가져오기 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        return self._article_list_below(session_key, board_name, heading_name, no, page_length, include_all_headings, LIST_ORDER_ROOT_ID)

    @require_login
    @log_method_call_important
    def vote_article(self, session_key, board_name, article_no):
        '''
        DB의 게시물 하나의 추천수를 증가시킴

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: BBS Name (u"" 을 주면 모든 게시판에 대하여)
        @type  article_no: integer
        @param article_no: Article No
        @rtype: void
        @return:
            1. 추천 성공: Nothing~
            2. 추천 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 로그인되지 않은 유저: InvalidOperation Exception
                3. 데이터베이스 오류: InrernalError Exception
        '''

        session = model.Session()
        board_id = None
        if smart_unicode(board_name) !=  u"":
            board_id = self.engine.board_manager.get_board_id(board_name)
        article = self._get_article(session, board_id, article_no)
        user = self._get_user(session, session_key)
        vote_unique_check_query = session.query(model.ArticleVoteStatus)
        if board_id:
            vote_unique_check_query = vote_unique_check_query.filter_by(user_id=user.id, board_id=board_id, article_id = article.id)
        else:
            vote_unique_check_query = vote_unique_check_query.filter_by(user_id=user.id, article_id = article.id)
        vote_unique_check = vote_unique_check_query.count()
        if vote_unique_check:
            session.close()
            raise InvalidOperation('ALREADY_VOTED')
        else:
            article.vote += 1
            vote = model.ArticleVoteStatus(user, article.board, article)
            session.add(vote)
            session.commit()
            session.close()

    @require_login
    @log_method_call_important
    def write_article(self, session_key, board_name, article_dic):
        '''
        DB에 게시글 하나를 작성함

        Article Dictionary { title, content, is_searchable, attach}

        @type  session_key: string
        @param session_key: User Key
        @type  article_dic: dictionary
        @param article_dic: Article Dictionary
        @type board_name: string
        @param board_name : BBS Name
        @rtype: string
        @return:
            1. Write 성공: Article Number
            2. Write 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 로그인되지 않은 유저: InvalidOperation Exception
                3. 읽기 전용 보드: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception
        '''

        user_ip = self.engine.login_manager.get_user_ip(session_key)

        session = model.Session()
        author = self._get_user(session, session_key)
        board = self.engine.board_manager._get_board_from_session(session, board_name)
        if not board.read_only:
            # 글에 적합한 heading 객체를 찾는다
            heading = None
            heading_str = smart_unicode(article_dic.heading)
            if heading_str != u"":
                heading = self.engine.board_manager._get_heading(session, board, heading_str)
            new_article = model.Article(board,
                                        heading,
                                        smart_unicode(article_dic.title),
                                        smart_unicode(article_dic.content),
                                        author,
                                        user_ip,
                                        None)
            session.add(new_article)
            if article_dic.__dict__.has_key('is_searchable'):
                if not article_dic.is_searchable:
                    new_article.is_searchable = False
            session.commit()
            id = new_article.id
            new_article.last_reply_id  = id
            session.commit()
            session.close()
        else:
            session.close()
            raise InvalidOperation('READ_ONLY_BOARD')
        return id

    @require_login
    @log_method_call_important
    def write_reply(self, session_key, board_name, article_no, reply_dic):
        '''
        댓글 하나를 해당하는 글에 추가

        Reply Dictionary { title, content }

        @type  session_key: string
        @param session_key: User Key
        @type  reply_dic: dictionary
        @param reply_dic: Reply Dictionary
        @type  board_name: string
        @param board_name: BBS Name
        @type article_no: integer
        @param article_no: Article No in which the reply will be added
        @rtype: string
        @return:
            1. 작성 성공: Article Number
            2. 작성 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 존재하지 않는 게시물: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception
        '''
        user_ip = self.engine.login_manager.get_user_ip(session_key)

        session = model.Session()
        author = self._get_user(session, session_key)
        board = self.engine.board_manager._get_board_from_session(session, board_name)
        article = self._get_article(session, board.id, article_no)

        heading = None
        heading_str = smart_unicode(reply_dic.heading)
        if heading_str != u"":
            heading = self.engine.board_manager._get_heading(session, board, heading_str)

        new_reply = model.Article(board,
                                heading,
                                smart_unicode(reply_dic.title),
                                smart_unicode(reply_dic.content),
                                author,
                                user_ip,
                                article)
        # XXX 2010.06.17.
        # 현재 root 글에 대해서만 정보를 저장할 것인가
        # 아니면 중간 중간에 걸쳐 있는 글에 대해서도 정보를 저장할 것인가
        # 고민이 필요하다. 즉 parent 들을 추적을 할까 말까에 대해서 ...
        article.reply_count += 1
        article.last_reply_date = new_reply.date
        if article.root:
            article.root.reply_count += 1
            article.root.last_reply_date = new_reply.date

        session.add(new_reply)
        session.commit()
        id = new_reply.id
        new_reply.last_reply_id = id
        article.last_reply_id = id
        if article.root:
            article.root.last_reply_id = new_reply.id
        session.commit()
        session.close()
        return id

    @require_login
    @log_method_call_important
    def modify_article(self, session_key, board_name, no, article_dic):
        '''
        DB의 해당하는 게시글 수정

        Article Dictionary { title, content, attach1, attach2 }
        attach1, attach2는 아직 구현되지 않음.

        @type  session_key: string
        @param session_key: User Key
        @type  no: integer
        @param no: Article Number
        @type  article_dic : dictionary
        @param article_dic : Article Dictionary
        @type board_name: string
        @param board_name : BBS Name
        @rtype: string
        @return:
            1. Modify 성공: Article Number
            2. Modify 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 수정 권한이 없음: InvalidOperation Exception
                5. 데이터베이스 오류: InternalError Exception 
        '''

        board_id = self.engine.board_manager.get_board_id(board_name)
        session = model.Session()
        author_id = self._get_user_id(session_key)
        article = self._get_article(session, board_id, no)
        if article.deleted == True:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        if article.author_id == author_id:
            article.title = smart_unicode(article_dic.title)
            article.content = smart_unicode(article_dic.content)
            # 필요한 경우에만 heading 수정
            new_heading = smart_unicode(article_dic.heading)
            cond1 = article.heading == None
            cond2 = new_heading == u''
            cond = not (cond1 and cond2)
            if not cond1:
                cond = (article.heading.heading != new_heading)
            if cond:
                heading = None
                if not cond2:
                    heading = self.engine.board_manager._get_heading_by_boardid(session, board_id, new_heading)
                article.heading = heading
            article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
            session.commit()
            id = article.id
            session.close()
        else:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        return id

    @require_login
    @log_method_call_important
    def delete_article(self, session_key, board_name, no):
        '''
        DB에 해당하는 글 삭제
        
        @type  session_key: string
        @param session_key: User Key
        @type board_name: string
        @param board_name : BBS Name
        @type  no: number
        @param no: Article Number
        @rtype: boolean 
        @return:
            1. Delete 성공: True
            2. Delete 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 수정 권한이 없음: InvalidOperation Exception
                5. 데이터베이스 오류: InternalError Exception
        '''

        board_id = self.engine.board_manager.get_board_id(board_name)
        session = model.Session()
        author = self._get_user(session, session_key)
        article = self._get_article(session, board_id, no)
        if article.author_id == author.id or author.is_sysop:
            if article.deleted:
                session.close()
                raise InvalidOperation("ALREADY_DELETED")
            article.deleted = True
            article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
            # root 가 있으면 root 의 댓글 수를 1 줄이면서 동시에 destroy 해버린다.
            if article.root:
                article.root.reply_count -= 1
                if article.root.reply_count == 0 and article.root.deleted:
                    article.root.destroyed = True
            # 스스로가 root 이고 reply 달렸던 것이 없으면 destroy 해버린다.
            elif article.reply_count == 0:
                article.destroyed = True
            session.commit()
            session.close()
        else:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        return True

    def _destroy_article(self, board_id, no):
        # XXX Internal use only
        session = model.Session()
        article = self._get_article(session, board_id, no)
        # 이미 destroyed 인 것은 고려할 필요가 없다.
        if article.destroyed:
            session.close()
            raise InvalidOperation("ALREADY_DESTROYED")
        # 현재의 DB 구조상의 한계로 인해, root가 아닌 글은 체크할 수 없다.
        if article.root == None and article.reply_count == 0:
            if article.deleted:
                # 이런 경우에만 일단 destroyed 를 set 해준다.
                article.destroyed = True
                session.commit()
            else:
                raise InvalidOperation("NOT_DELETED")
        else:
            session.close()
            raise InvalidOperation("NOT_IMPLEMENTED")
        session.close()

    @require_login
    @log_method_call_important
    def destroy_article(self, session_key, board_name, no):
        '''
        주어진 글이 Destroy 할만한 글인지 판단하여, 만일 그렇다면 Destroy 함.
        
        @type  session_key: string
        @param session_key: User Key
        @type board_name: string
        @param board_name : BBS Name
        @type  no: number
        @param no: Article Number
        @rtype: boolean 
        @return:
            1. Delete 성공: True
            2. Delete 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 수정 권한이 없음: InvalidOperation Exception
                5. 데이터베이스 오류: InternalError Exception
                6. 기타 : 이 주석은 전부 뜯어고쳐야 함.
        '''

        session = model.Session()
        user = self._get_user(session, session_key)
        session.close()
        # 시삽만 이 작업을 할 수 있다.
        if user.is_sysop:
            board_id = self.engine.board_manager.get_board_id(board_name)
            self._destroy_article(board_id, no)
        else:
            raise InvalidOperation("NO_PERMISSION")
        return True

    def _fix_article_concurrency(self, board_id, no):
        '''Internal use only.'''
        session = model.Session()
        article = session.query(model.Article).options(eagerload('children')).filter_by(id=no).one()

        if article.root != None:
            session.close()
            raise InvalidOperation("NOT_IMPLEMENTED")

        last_reply_id   = article.id
        last_reply_date = article.last_modified_date
        reply_count     = 0
        # 주어진 글을 순회하며, 실제 reply count, last_reply_id, last_reply_date 구한다.
        stack = []
        stack.append(article)
        while stack:
            art = stack.pop()
            for child in art.children[::-1]:
                if not child.deleted:
                    reply_count += 1
                    if last_reply_id < child.id:
                        last_reply_id = child.id
                    if last_reply_date < child.last_reply_date:
                        last_reply_date = child.last_reply_date
                stack.append(child)

        try:
            if article.reply_count != reply_count:
                article.reply_count = reply_count
            if (not article.destroyed) and article.deleted and (article.reply_count == 0):
                article.destroyed = True
            if article.last_reply_id != last_reply_id:
                article.last_reply_id = last_reply_id
            if article.last_reply_date != last_reply_date:
                article.last_reply_date = last_reply_date

            session.commit()
            session.close()

        except InvalidRequestError:
            session.rollback()
            session.close()
            raise InvalidOperation("Internal Error")

    @require_login
    @log_method_call_important
    def fix_article_concurrency(self, session_key, board_name, no):
        '''
        주어진 글의 concurrency 가 올바른지 확인.
        올바르지 않다면 이를 고침.
        
        @type  session_key: string
        @param session_key: User Key
        @type board_name: string
        @param board_name : BBS Name
        @type  no: number
        @param no: Article Number
        @rtype: boolean 
        @return:
            1. Fix 성공: True
            2. Fix 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 수정 권한이 없음: InvalidOperation Exception
                5. 데이터베이스 오류: InternalError Exception
                6. 기타 : 이 주석은 전부 뜯어고쳐야 함.
        '''

        session = model.Session()
        user = self._get_user(session, session_key)
        session.close()
        # 시삽만 이 작업을 할 수 있다.
        if user.is_sysop:
            board_id = self.engine.board_manager.get_board_id(board_name)
            return self._fix_article_concurrency(board_id, no)
        else:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        return True

# vim: set et ts=8 sw=4 sts=4
