# -*- coding: utf-8 -*-
import datetime
import time
import xmlrpclib
import logging

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import eagerload
from arara import model
from arara.util import require_login, filter_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import datetime2timestamp
from arara.util import smart_unicode
from arara.server import get_server

from arara_thrift.ttypes import *

log_method_call = log_method_call_with_source('article_manager')
log_method_call_important = log_method_call_with_source_important('article_manager')

WRITE_ARTICLE_DICT = ('title', 'content')
READ_ARTICLE_WHITELIST = ('id', 'title', 'content', 'last_modified_date', 'deleted', 'blacklisted', 'author_username', 'author_nickname', 'vote', 'date', 'hit', 'depth', 'root_id', 'is_searchable', 'attach')
LIST_ARTICLE_WHITELIST = ('id', 'title', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'vote', 'hit')
SEARCH_ARTICLE_WHITELIST = ('id', 'title', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'vote', 'hit', 'content')
BEST_ARTICLE_WHITELIST = ('id', 'title', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'vote', 'hit', 'last_page', 'board_name')

class ArticleManager(object):
    '''
    게시글 및 검색 처리 클래스
    현재 게시글 표시방식이 절묘하기 때문에 read 메소드에 관한 논의가 필요.

    용법 : arara/test/article_manager.txt
    '''
    def __init__(self):
        pass
        #monk data
        #self.articles = {'garbages': {} }
        #self.article_no = 0

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _set_blacklist_manager(self, blacklist_manager):
        self.blacklist_manager = blacklist_manager 

    def _set_read_status_manager(self, read_status_manager):
        self.read_status_manager = read_status_manager
    
    def _set_board_manager(self, board_manager):
        self.board_manager = board_manager

    def _set_file_manager(self, file_manager):
        self.file_manager = file_manager

    def _get_board(self, session, board_name):
        try:
            board = session.query(model.Board).filter_by(board_name=smart_unicode(board_name)).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation("BOARD_NOT_EXIST")
        return board

    def _get_board_id(self, session, board_name):
        return self._get_board(session, board_name).id

    def _article_thread_to_list(self, article_thread, session_key, blacklist_users):
        queue = []
        depth_ret = {}
        queue.append({article_thread: 1})
        while queue:
            for item in queue:
                depth = item.values()[0]
                depth_ret[item.keys()[0]] = depth
            depth += 1
            for i in xrange(len(queue)):
                parent_article = queue.pop(0).keys()[0]
                for child in parent_article.children:
                    queue.append({child: depth})
        stack = []
        ret = []
        stack.append(article_thread)
        article_id_list = []
        while stack:
            a = stack.pop()
            d = self._get_dict(a, READ_ARTICLE_WHITELIST)
            d['depth'] = depth_ret[a]

            if d['author_username'] in blacklist_users:
                d['blacklisted'] = True
            else:
                d['blacklisted'] = False
            article_id_list.append(d['id'])
            d['date'] = datetime2timestamp(d['date'])
            d['last_modified_date'] = datetime2timestamp(d['last_modified_date'])
            ret.append(Article(**d))
            for child in a.children[::-1]:
                stack.append(child)
        get_server().read_status_manager.mark_as_read_list(session_key, article_id_list)
        return ret

    def _get_best_article(self, session_key, board_id, count, time_to_filter, best_type):
        session = model.Session()
        time_to_filter = datetime.datetime.fromtimestamp(time.time()-time_to_filter)
        if board_id:
            query = session.query(model.Article).filter(and_(
                    model.articles_table.c.board_id==board_id,
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > time_to_filter,
                    not_(model.articles_table.c.deleted==True)))
        else:
            query = session.query(model.Article).filter(and_(
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > time_to_filter,
                    not_(model.articles_table.c.deleted==True)))
        best_article = query.order_by(model.Article.vote.desc()).order_by(model.Article.reply_count.desc()).order_by(model.Article.id.desc())[:count]
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
            del item_dict['author_id']
        if item_dict.has_key('board_id'):
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
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
        user_info = get_server().login_manager.get_session(session_key)
        try:
            user = session.query(model.User).filter_by(username=smart_unicode(user_info.username)).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('user does not exist')
        return user

    def _get_user_id(self, session_key):
        return get_server().login_manager.get_user_id(session_key)

    def _get_article(self, session, board_id, article_id):
        try:
            article = session.query(model.Article).filter_by(board_id=board_id, id=article_id).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation("article does not exist")
        return article

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
        session = model.Session()
        board_id = self._get_board_id(session, board_name)
        session.close()

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
        session = model.Session()
        board_id = self._get_board_id(session, board_name)
        session.close()

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
            read_stats_list = get_server().read_status_manager.check_stats(session_key, article_number)
            #not_read_article = filter(lambda x : x = 'N', read_stats_list) 
            not_read_article_number = []
            for i in range(len(read_stats_list)):
                if read_stats_list[i] == 'N':
                    not_read_article_number.append(article_number[i])
            article_count = len(not_read_article_number) 
            last_page = int(article_count / page_length)
            if article_count % page_length != 0:
                last_page += 1
            elif article_count == 0:
                last_page += 1
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
            last_page = int(article_count / page_length)
            if article_count % page_length != 0:
                last_page += 1
            elif article_count == 0:
                last_page += 1
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


    def _get_blacklist_users(self, session_key):
        try:
            blacklist_dict_list = get_server().blacklist_manager.list_(session_key)
        except NotLoggedIn:
            blacklist_dict_list = []
            pass
        return set([x.blacklisted_user_username for x in blacklist_dict_list if x.block_article])

    def _get_article_list(self, session_key, board_name, page, page_length):
        session = model.Session()
        board_id = self._get_board_id(session, board_name)
        article_count = session.query(model.Article).filter_by(board_id=board_id, root_id=None).count()
        last_page = int(article_count / page_length)
        if article_count % page_length != 0:
            last_page += 1
        elif article_count == 0:
            last_page += 1
        if page > last_page:
            session.close()
            raise InvalidOperation('WRONG_PAGENUM')
        offset = page_length * (page - 1)
        last = offset + page_length
        article_list = list(session.query(model.Article).filter_by(board_id=board_id, root_id=None).order_by(model.Article.id.desc())[offset:last])
        session.close()
        article_dict_list = self._get_dict_list(article_list, LIST_ARTICLE_WHITELIST)
        return article_dict_list, last_page, article_count

    @log_method_call
    def article_list(self, session_key, board_name, page=1, page_length=20):
        '''
        게시판의 게시글 목록 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @type board_name: string
        @param board_name : BBS Name
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: Article List
            2. 리스트 읽어오기 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 페이지 번호 오류: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception 
        '''
        blacklist_users = self._get_blacklist_users(session_key)

        article_dict_list, last_page, article_count = self._get_article_list(session_key, board_name, page, page_length)
        # InvalidOperation(board not exist) 는 여기서 알아서 불릴 것이므로 제거.

        article_list = ArticleList()
        article_list.hit = list()

        # article_dict_list 를 generator 에서 list화.
        # 어차피 이 함수가 끝날때까지 append 되는 새 list 를 return 하므로 상관없다.
        article_dict_list = [x for x in article_dict_list]
        article_id_list = [article['id'] for article in article_dict_list]
        read_stats_list = None # Namespace 에 등록. Assign 은 요 바로 다음에서.

        try:
            read_stats_list = get_server().read_status_manager.check_stats(session_key, article_id_list)
        except NotLoggedIn, InvalidOperation:
            read_stats_list = ['N'] * len(article_id_list)

        for idx, article in enumerate(article_dict_list):
            if article['author_username'] in blacklist_users:
                article['blacklisted'] = True
            else:
                article['blacklisted'] = False
            if not article.has_key('type'):
                article['type'] = 'normal'

            article['read_status'] = read_stats_list[idx]

            article['date'] = datetime2timestamp(article['date'])
            article['last_modified_date'] = datetime2timestamp(article['last_modified_date'])
            article_list.hit.append(Article(**article))

        article_list.last_page = last_page
        article_list.results = article_count
        return article_list
         
    @require_login
    @log_method_call_important
    def read(self, session_key, board_name, no):
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
        self._get_board(session, board_name)
        blacklist_dict_list = get_server().blacklist_manager.list_(session_key)
        blacklist_users = set([x.blacklisted_user_username for x in blacklist_dict_list if x.block_article])

        try:
            article = session.query(model.Article).options(eagerload('children')).filter_by(id=no).one()
            msg = get_server().read_status_manager.check_stat(session_key, no)
            if msg == 'N':
                article.hit += 1
                session.commit()
        except InvalidRequestError:
            session.rollback()
            session.close()
            raise InvalidOperation('ARTICLE_NOT_EXIST')
        article_dict_list = self._article_thread_to_list(article, session_key, blacklist_users)
        session.close()
        return article_dict_list

    @require_login
    @log_method_call
    def article_list_below(self, session_key, board_name, no, page_length=20):
        '''
        게시물을 읽을 때 밑에 표시될 게시글 목록을 가져오는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @type  no: integer
        @param no: Article No
        @type  page_length: integer
        @param page_length: Number of articles to be displayed on a page
        @rtype: Article List
        @return:
            1. 목록 가져오기 성공: Article List
            2. 목록 가져오기 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception

        '''
        session = model.Session()
        board_id = self._get_board_id(session, board_name)
        total_article_count = session.query(model.Article).filter_by(board_id=board_id, root_id=None).count()
        remaining_article_count = session.query(model.Article).filter(and_(
                model.articles_table.c.board_id==board_id,
                model.articles_table.c.root_id==None,
                model.articles_table.c.id < no)).count()
        position_no = total_article_count - remaining_article_count
        session.close()

        page_position = 0
        # XXX (combacsa): WTF below? ;;;
        while True:
            page_position += 1
            if position_no <= (page_length * page_position):
                break
        try:
            below_article_dict_list = self.article_list(session_key, board_name, page_position, page_length)
        except Exception:
            raise

        ret = ArticleList()
        ret.hit = below_article_dict_list.hit
        ret.current_page = page_position
        ret.last_page = below_article_dict_list.last_page
        ret.results = below_article_dict_list.results
        return ret
        

    @require_login
    @log_method_call_important
    def vote_article(self, session_key, board_name, article_no):
        '''
        DB의 게시물 하나의 추천수를 증가시킴

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: BBS Name
        @type  article_no: integer
        @param article_no: Article No
        @rtype: boolean
        @return:
            1. 추천 성공: True
            2. 추천 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 로그인되지 않은 유저: InvalidOperation Exception
                3. 데이터베이스 오류: InrernalError Exception
        '''

        session = model.Session()
        board = self._get_board(session, board_name)
        article = self._get_article(session, board.id, article_no)
        user = self._get_user(session, session_key)
        vote_unique_check = session.query(model.ArticleVoteStatus).filter_by(user_id=user.id, board_id=board.id, article_id = article.id).count()
        if vote_unique_check:
            session.close()
            raise InvalidOperation('ALREADY_VOTED')
        else:
            article.vote += 1
            vote = model.ArticleVoteStatus(user, board, article)
            session.add(vote)
            session.commit()
            session.close()
            return

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

        user_info = get_server().login_manager.get_session(session_key)

        session = model.Session()
        author = self._get_user(session, session_key)
        board = self._get_board(session, board_name)
        if not board.read_only:
            new_article = model.Article(board,
                                        smart_unicode(article_dic.title),
                                        smart_unicode(article_dic.content),
                                        author,
                                        user_info.ip,
                                        None)
            session.add(new_article)
            if article_dic.__dict__.has_key('is_searchable'):
                if not article_dic.is_searchable:
                    new_article.is_searchable = False
            session.commit()
            id = new_article.id
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


        user_info = get_server().login_manager.get_session(session_key)

        session = model.Session()
        author = self._get_user(session, session_key)
        board = self._get_board(session, board_name)
        article = self._get_article(session, board.id, article_no)
        new_reply = model.Article(board,
                                smart_unicode(reply_dic.title),
                                smart_unicode(reply_dic.content),
                                author,
                                user_info.ip,
                                article)
        article.reply_count += 1
        if article.root:
            article.root.reply_count += 1
        session.add(new_reply)
        session.commit()
        id = new_reply.id
        session.close()
        return id

    @require_login
    @log_method_call_important
    def modify(self, session_key, board_name, no, article_dic):
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

        session = model.Session()
        author = self._get_user(session, session_key)
        board_id = self._get_board_id(session, board_name)
        article = self._get_article(session, board_id, no)
        if article.deleted == True:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        if article.author_id == author.id:
            article.title = smart_unicode(article_dic.title)
            article.content = smart_unicode(article_dic.content)
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
    def delete_(self, session_key, board_name, no):
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

        session = model.Session()
        author = self._get_user(session, session_key)
        board_id = self._get_board_id(session, board_name)
        article = self._get_article(session, board_id, no)
        if article.author_id == author.id or author.is_sysop:
            if article.deleted:
                session.close()
                raise InvalidOperation("ALREADY_DELETED")
            article.deleted = True
            article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
            if article.root:
                article.root.reply_count -= 1
            session.commit()
            session.close()
        else:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        return True

# vim: set et ts=8 sw=4 sts=4
