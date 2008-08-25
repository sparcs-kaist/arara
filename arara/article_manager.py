# -*- coding: utf-8 -*-
import datetime
import time
import xmlrpclib

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import and_, or_, not_
from arara import model
from arara.util import require_login, filter_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important

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

class NotLoggedIn(Exception):
    pass

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

    def _is_board_exist(self, board_name):
        ret, _ = self.board_manager.get_board(board_name)
        if ret:
            return True, 'OK'
        else:
            return False, 'BOARD_NOT_EXIST'

    def _article_thread_to_list(self, article_thread):
        stack = []
        ret = []
        stack.append((article_thread, 1))
        while stack:
            a, depth = stack.pop()
            d = self._get_dict(a, READ_ARTICLE_WHITELIST)
            d['depth'] = depth
            ret.append(filter_dict(d, READ_ARTICLE_WHITELIST))
            for child in a.children[::-1]:
                if depth < 12:
                    depth += 1
                stack.append((child, depth))
        return ret

    def _get_today_best_article(self, session_key, board=None, count=5):
        session = model.Session()
        # 1 day is 86400 sec
        time_to_filter = datetime.datetime.fromtimestamp(time.time()-86400)
        if board:
            today_best_article = session.query(model.Article).filter(and_(
                    model.articles_table.c.board_id==board.id,
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > time_to_filter,
                    not_(model.articles_table.c.deleted==True))
                    )[:count].order_by(model.Article.vote.desc()).order_by(model.Article.reply_count.desc()).order_by(model.Article.id.desc()).all()
            today_best_article_dict_list = self._get_dict_list(today_best_article, BEST_ARTICLE_WHITELIST)
            for article in today_best_article_dict_list:
                article['type'] = 'today'
            session.close()
            return True, today_best_article_dict_list
        else:
            today_best_article = session.query(model.Article).filter(and_(
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > time_to_filter,
                    not_(model.articles_table.c.deleted==True))
                    )[:count].order_by(model.Article.vote.desc()).order_by(model.Article.reply_count.desc()).order_by(model.Article.id.desc()).all()
            today_best_article_dict_list = self._get_dict_list(today_best_article, BEST_ARTICLE_WHITELIST)
            for article in today_best_article_dict_list:
                article['type'] = 'today'
            session.close()
            return True, today_best_article_dict_list

    def _get_weekly_best_article(self, session_key, board=None, count=5):
        session = model.Session()
        # 1 week is 604800 sec
        time_to_filter = datetime.datetime.fromtimestamp(time.time()-604800)
        if board:
            weekly_best_article = session.query(model.Article).filter(and_(
                    model.articles_table.c.board_id==board.id,
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > time_to_filter,
                    not_(model.articles_table.c.deleted==True))
                    )[:count].order_by(model.Article.vote.desc()).order_by(model.Article.reply_count.desc()).order_by(model.Article.id.desc()).all()
            weekly_best_article_dict_list = self._get_dict_list(weekly_best_article, BEST_ARTICLE_WHITELIST)
            for article in weekly_best_article_dict_list:
                article['type'] = 'weekly'
            session.close()
            return True, weekly_best_article_dict_list
        else:
            weekly_best_article = session.query(model.Article).filter(and_(
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > time_to_filter,
                    not_(model.articles_table.c.deleted==True))
                    )[:count].order_by(model.Article.vote.desc()).order_by(model.Article.reply_count.desc()).order_by(model.Article.id.desc()).all()
            weekly_best_article_dict_list = self._get_dict_list(weekly_best_article, BEST_ARTICLE_WHITELIST)
            for article in weekly_best_article_dict_list:
                article['type'] = 'weekly'
            session.close()
            return True, weekly_best_article_dict_list

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        session = model.Session()
        if item_dict.has_key('author_id'):
            item_dict['author_username'] = item.author.username
            item_dict['author_nickname'] = item.author.nickname
            del item_dict['author_id']
        if item_dict.has_key('board_id'):
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
        if item_dict.has_key('root_id'):
            if not item_dict['root_id']:
                item_dict['root_id'] = item_dict['id']
        if item_dict.has_key('content'):
            if whitelist == SEARCH_ARTICLE_WHITELIST:
                item_dict['content'] = item_dict['content'][:40]
            if whitelist == READ_ARTICLE_WHITELIST:
                attach_files = session.query(model.File).filter_by(
                        article_id=item.id).filter_by(deleted=False).all()
                if len(attach_files) > 0:
                    item_dict['attach'] = []
                    for one_file in attach_files:
                        one_file_dict = one_file.__dict__
                        item_dict['attach'].append({'filename': one_file_dict['filename'],
                                                    'file_id': one_file_dict['id']})
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        session.close()
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(filtered_dict)
        return return_list

    @log_method_call
    def get_today_best_list(self, count=5):
        '''
        전체 보드에서 투베를 가져오는 함수

        @type  count: integer
        @param count: Number of today's best articles to get
        @rtype: list
        @return:
            1. 투베를 가져오는데 성공: True, Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret, today_best_list = self._get_today_best_article(None, None, count)

        if ret:
            return True, today_best_list
        else:
            return False, 'DATABASE_ERROR'

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
            1. 투베를 가져오는데 성공: True, Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: False, 'BOARD_NOT_EXIST'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        session = model.Session()
        try:
            board = session.query(model.Board).filter_by(board_name=board_name).one()
        except InvalidRequestError:
            return False, 'BOARD_NOT_EXIST'
        session.close()
        ret, today_best_list = self._get_today_best_article(None, board, count)

        if ret:
            return True, today_best_list
        else:
            return False, 'DATABASE_ERROR'

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
            1. 투베를 가져오는데 성공: True, Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: False, 'BOARD_NOT_EXIST'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret, weekly_best_list = self._get_weekly_best_article(None, None, count)

        if ret:
            return True, weekly_best_list
        else:
            return False, 'DATABASE_ERROR'

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
            1. 투베를 가져오는데 성공: True, Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: False, 'BOARD_NOT_EXIST'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        session = model.Session()
        try:
            board = session.query(model.Board).filter_by(board_name=board_name).one()
        except InvalidRequestError:
            return False, 'BOARD_NOT_EXIST'
        session.close()
        ret, weekly_best_list = self._get_weekly_best_article(None, board, count)

        if ret:
            return True, weekly_best_list
        else:
            return False, 'DATABASE_ERROR'
        
    @require_login
    def not_read_article_list(self, session_key, page=1, page_length=20)
        '''
        사용자가 안 읽은 글들을 불러오는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, list
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: boolean, list
        @return:
            1. 리스트 읽어오기 성공: True, Not Read Article List
            2. 리스트 읽어오기 실패:
                1. 페이지 번호 오류: False, 'WRONG_PAGENUM' 
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret_dict = {}
        try:
            session = model.Session()
            article_count = session.query(model.Article).filter_by(root_id=None).count()
            last_page = int(article_count / page_length)
            if article_count % page_length != 0:
                last_page += 1
            elif article_count == 0:
                last_page += 1
            if page > last_page:
                session.close()
                return False, 'WRONG_PAGENUM'
            offset = page_length * (page - 1)
            last = offset + page_length
            article_list = session.query(model.Article).filter_by(root_id=None)[offset:last].order_by(model.Article.id.desc()).all()
            article_dict_list = self._get_dict_list(article_list, LIST_ARTICLE_WHITELIST)
            for article in article_dict_list:
                ret, msg = self.read_status_manager.check_stat(session_key, board_name, article['id'])
                if ret:
                    article['read_status'] = msg
            ret_dict['hit'] = article_dict_list
            ret_dict['last_page'] = last_page
            ret_dict['results'] = article_count 
            session.close()
            return True, ret_dict
        except InvalidRequestError:
            raise
            session.close()
            return False, 'DATABASE_ERROR'



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
        @rtype: boolean, list
        @return:
            1. 리스트 읽어오기 성공: True, New Article List
            2. 리스트 읽어오기 실패:
                1. 페이지 번호 오류: False, 'WRONG_PAGENUM' 
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret_dict = {}
        _, user_info = self.login_manager.get_session(session_key)

        try:
            session = model.Session()
            user = session.query(model.User).filter_by(username=user_info['username']).one()
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
                return False, 'WRONG_PAGENUM'
            offset = page_length * (page - 1)
            last = offset + page_length

            article_list = session.query(model.Article).filter(and_(
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.last_modified_date > user.last_logout_time))[offset:last].order_by(model.Article.id.desc()).all()
            article_dict_list = self._get_dict_list(article_list, LIST_ARTICLE_WHITELIST)
            for article in article_dict_list:
                    article['read_status'] = 'N'
            ret_dict['hit'] = article_dict_list
            ret_dict['last_page'] = last_page
            ret_dict['results'] = article_count
            session.close()
            return True, ret_dict
        except InvalidRequestError:
            raise
            session.close()
            return False, 'DATABASE_ERROR'


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
        @rtype: boolean, list
        @return:
            1. 리스트 읽어오기 성공: True, Article List
            2. 리스트 읽어오기 실패:
                1. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                2. 페이지 번호 오류: False, 'WRONG_PAGENUM' 
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret_dict = {}

        try:
            session = model.Session()
            ret, _ = self._is_board_exist(board_name)
            if ret:
                board = session.query(model.Board).filter_by(board_name=board_name).one()
                article_count = session.query(model.Article).filter_by(board_id=board.id, root_id=None).count()
                last_page = int(article_count / page_length)
                if article_count % page_length != 0:
                    last_page += 1
                elif article_count == 0:
                    last_page += 1
                if page > last_page:
                    session.close()
                    return False, 'WRONG_PAGENUM'
                offset = page_length * (page - 1)
                last = offset + page_length
                article_list = session.query(model.Article).filter_by(board_id=board.id, root_id=None)[offset:last].order_by(model.Article.id.desc()).all()
                article_dict_list = self._get_dict_list(article_list, LIST_ARTICLE_WHITELIST)
                for article in article_dict_list:
                    if article.has_key('id'):
                        if not article.has_key('type'):
                            article['type'] = 'normal'
                        ret, msg = self.read_status_manager.check_stat(session_key, board_name, article['id'])
                        if ret:
                            article['read_status'] = msg
                ret_dict['hit'] = article_dict_list
                ret_dict['last_page'] = last_page
                ret_dict['results'] = article_count 
                session.close()
                return True, ret_dict
            else:
                session.close()
                return ret, 'BOARD_NOT_EXIST'
        except InvalidRequestError:
            raise
            session.close()
            return False, 'DATABASE_ERROR'
             
    @require_login
    @log_method_call
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
        @rtype: boolean, dictionary
        @return:
            1. Read 성공: True, Article Dictionary
            2. Read 실패:
                1. 존재하지 않는 게시물번호: False, 'ARTICLE_NOT_EXIST'
                2. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                3. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                4. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        _, user_info = self.login_manager.get_session(session_key)
        ret, message = self._is_board_exist(board_name)
        
        if ret:
            session = model.Session()
            board = session.query(model.Board).filter_by(board_name=board_name)
            user = session.query(model.User).filter_by(username=user_info['username']).one()
            _, blacklist_dict_list = self.blacklist_manager.list(session_key)
            blacklist_users = set()
            for blacklist_item in blacklist_dict_list:
                if blacklist_item['block_article']:
                    blacklist_users.add(blacklist_item['blacklisted_user_username'])
            try:
                article = session.query(model.Article).filter_by(id=no).one()
                ret, msg = self.read_status_manager.check_stat(session_key, board_name, no)
                if ret:
                    if msg == 'N':
                        article.hit += 1
                        session.commit()
            except InvalidRequestError:
                session.rollback()
                session.close()
                return False, 'ARTICLE_NOT_EXIST'
            article_dict_list = self._article_thread_to_list(article)
            for item in article_dict_list:
                if item['author_username'] in blacklist_users:
                    item['blacklisted'] = True
                else:
                    item['blacklisted'] = False
                ret, msg = self.read_status_manager.mark_as_read(session_key, board_name, item['id'])
                if not ret:
                    session.close()
                    return ret, msg
            session.close()
            return True, article_dict_list
        else:
            return ret, message

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
        '''
        ret_dict = {}
        ret, user_info = self.login_manager.get_session(session_key)
        ret, message = self._is_board_exist(board_name)

        if ret:
            session = model.Session()
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            total_article_count = session.query(model.Article).filter_by(board_id=board.id, root_id=None).count()
            remaining_article_count = session.query(model.Article).filter(and_(
                    model.articles_table.c.board_id==board.id,
                    model.articles_table.c.root_id==None,
                    model.articles_table.c.id < no)).count()
            position_no = total_article_count - remaining_article_count
            page_position = 0
            while True:
                page_position += 1
                if position_no <= (page_length * page_position):
                    break
            ret, below_article_dict_list = self.article_list(session_key, board_name, page_position, page_length)
            if ret:
                ret_dict['hit'] = below_article_dict_list['hit']
                ret_dict['current_page'] = page_position
                ret_dict['results'] = article_count 
                session.close()
                return True, ret_dict
            else:
                session.close()
                return False, 'DATABASE_ERROR'
        else:
            return False, 'BOARD_NOT_EXIST'
        

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
        @rtype: boolean, string
        @return:
            1. 추천 성공: True, 'OK'
            2. 추천 실패:
                1. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        ret, message = self._is_board_exist(board_name)
        if ret:
            session = model.Session()
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            try:
                article = session.query(model.Article).filter_by(id=article_no).one()
            except InvalidRequestError:
                session.close()
                return False, 'ARTICLE_NOT_EXIST'
            user = session.query(model.User).filter_by(username=user_info['username']).one()
            vote_unique_check = session.query(model.ArticleVoteStatus).filter_by(user_id=user.id, board_id=board.id, article_id = article.id).all()
            if vote_unique_check:
                session.close()
                return False, 'ALREADY_VOTED'
            else:
                article.vote += 1
                vote = model.ArticleVoteStatus(user, board, article)
                session.save(vote)
                session.commit()
                session.close()
                return True, 'OK'
        else:
            return False, message

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
        @rtype: boolean, string
        @return:
            1. Write 성공: True, Article Number
            2. Write 실패:
                1. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 읽기 전용 보드: False, 'READ_ONLY_BOARD'
                4. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        ret, message = self._is_board_exist(board_name)
        if ret:
            session = model.Session()
            author = session.query(model.User).filter_by(username=user_info['username']).one()
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            if not board.read_only:
                new_article = model.Article(board,
                                            article_dic['title'],
                                            article_dic['content'],
                                            author,
                                            user_info['ip'],
                                            None)
                session.save(new_article)
                if article_dic.has_key('is_searchable'):
                    if not article_dic['is_searchable']:
                        new_article.is_searchable = False
                session.commit()
                session.close()
            else:
                session.close()
                return False, 'READ_ONLY_BOARD'
        else:
            return ret, message
        return True, new_article.id

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
        @rtype: boolean, string
        @return:
            1. 작성 성공: True, Article Number
            2. 작성 실패:
                1. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                2. 존재하지 않는 게시물: False, 'ARTICLE_NOT_EXIST'
                3. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                4. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''


        ret, user_info = self.login_manager.get_session(session_key)
        ret, message = self._is_board_exist(board_name)
        if ret:
            session = model.Session()
            author = session.query(model.User).filter_by(username=user_info['username']).one()
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            try:
                article = session.query(model.Article).filter_by(board_id=board.id, id=article_no).one()
                new_reply = model.Article(board,
                                        reply_dic['title'],
                                        reply_dic['content'],
                                        author,
                                        user_info['ip'],
                                        article)
                article.reply_count += 1
                session.save(new_reply)
                session.commit()
                session.close()
            except InvalidRequestError:
                session.close()
                return False, 'ARTICLE_NOT_EXIST'
        else:
            return ret, message
        return True, new_reply.id

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
        @rtype: boolean, string
        @return:
            1. Modify 성공: True, Article Number
            2. Modify 실패:
                1. 존재하지 않는 게시물번호: False, 'ARTICLE_NOT_EXIST'
                2. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                3. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                4. 수정 권한이 없음: False, 'NO_PERMISSION'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        ret, message = self._is_board_exist(board_name)
        if ret:
            session = model.Session()
            author = session.query(model.User).filter_by(username=user_info['username']).one()
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            try:
                article = session.query(model.Article).filter_by(board_id=board.id, id=no).one()
                if article.deleted == True:
                    session.close()
                    return False, "NO_PERMISSION"
                if article.author_id == author.id:
                    article.title = article_dic['title']
                    article.content = article_dic['content']
                    article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
                    session.commit()
                    session.close()
                else:
                    session.close()
                    return False, "NO_PERMISSION"
            except InvalidRequestError:
                session.close()
                return False, "ARTICLE_NOT_EXIST"
        else:
            return ret, message
        return True, article.id

    @require_login
    @log_method_call_important
    def delete(self, session_key, board_name, no):
        '''
        DB에 해당하는 글 삭제
        
        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type board_name: string
        @param board_name : BBS Name
        @rtype: boolean, string 
        @return:
            1. Delete 성공: True, 'OK'
            2. Delete 실패:
                1. 존재하지 않는 게시물번호: False, 'ARTICLE_NOT_EXIST'
                2. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                3. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                4. 수정 권한이 없음: False, 'NO_PERMISSION'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        ret, message = self._is_board_exist(board_name)
        if ret:
            session = model.Session()
            author = session.query(model.User).filter_by(username=user_info['username']).one()
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            try:
                article = session.query(model.Article).filter_by(board_id=board.id, id=no).one()
                if article.author_id == author.id:
                    article.deleted = True
                    article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
                    if article.root:
                        article.root.reply_count -= 1
                    session.commit()
                    session.close()
                else:
                    session.close()
                    return False, "NO_PERMISSION"
            except InvalidRequestError:
                session.close()
                return False, "ARTICLE_NOT_EXIST"
        else:
            return ret, message
        return True, article.id

    @log_method_call
    def board_list(self, session_key):
        '''
        게시판 목록 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, dictionary
        @return:
            1. 리스트 읽어오기 성공: True, Dictionary of boards with new article num(not implemented)
            2. 리스트 읽어오기 실패: False 
                1. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret, board_list = self.board_manager.get_board_list()
        if ret:
            return True, board_list
        else:
            return False, 'DATABASE_ERROR'

    @require_login
    @log_method_call_important
    def search(self, session_key, board_name, query_text, search_type='All', page=1, page_length=20):
        '''
        게시물 검색

        검색 type이 all일 때 board_name을 지정하면 그 보드의 전체 검색결과를,
        
        board_name에 'all_board'를 넣으면 전체 보드를 검색한 결과를 리턴한다.

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: BBS Name
        @type  query_text: string
        @param query_text: Text to Search
        @type  search_type: string
        @param search_type: Search Type (Title, Content, Author_nick, Author_username, Date, All)
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: boolean, list
        @return:
            1. 검색 성공: True, Article List(리스트의 맨 첫 항목은 검색 결과수)
            2. 검색 실패:
                1. 검색 결과가 존재하지 않음: False, 'NOT_FOUND'
                2. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                3. 잘못된 페이지 번호: False, 'WROND_PAGENUM'
                4. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'

        '''
        ret, user_info = self.login_manager.get_session(session_key)
        session = model.Session()
        board_name = unicode(board_name)
        query_text = unicode(query_text)
        db_query_text = unicode('%' + query_text + '%')
        if search_type.upper() == 'ALL':
            if board_name.upper() == 'ALL_BOARD':
                board_name = None
            else:
                ret = self._is_board_exist(board_name)
                if not ret:
                    session.close()
                    return False, 'BOARD_NOT_EXIST'
                else:
                    board = session.query(model.Board).filter_by(board_name=board_name).one()
        else:
            board = session.query(model.Board).filter_by(board_name=board_name).one()

        ret_dict = {}

        if search_type.upper() == 'ALL':
            if not board_name:
                search_manager = xmlrpclib.Server('http://nan.sparcs.org:9000/api')
                query = str(query_text) + ' source:ara'
                result = search_manager.search('00000000000000000000000000000000',query)
                for one_result in result['hits']:
                    if one_result.has_key('uri'):
                        parsed_uri = one_result['uri'].rsplit('/', 2)
                        one_result['id'] = parsed_uri[::-1][0]
                        one_result['board_name'] = parsed_uri[::-1][1]
                session.close()
                return True, result
            else:
                start_time = time.time()
                if board_name:
                    article_count = session.query(model.Article).join('author').filter(and_(or_(
                            model.articles_table.c.title.like(db_query_text),
                            model.articles_table.c.content.like(db_query_text),
                            model.User.username.like(db_query_text)),
                            model.articles_table.c.board_id == board.id,
                            not_(model.articles_table.c.is_searchable == False))).count()
                else:
                    article_count = session.query(model.Article).join('author').filter(and_(or_(
                            model.articles_table.c.title.like(db_query_text),
                            model.articles_table.c.content.like(db_query_text),
                            model.User.username.like(db_query_text)),
                            not_(model.articles_table.c.is_searchable == False))).count()
                last_page = int(article_count / page_length)
                if article_count % page_length != 0:
                    last_page += 1
                elif article_count == 0:
                    last_page += 1
                if page > last_page:
                    session.close()
                    return False, 'WRONG_PAGENUM'
                offset = page_length * (page - 1)
                last = offset + page_length
                if board_name:
                    result = session.query(model.Article).join('author').filter(and_(or_(
                            model.articles_table.c.title.like(db_query_text),
                            model.articles_table.c.content.like(db_query_text),
                            model.User.username.like(db_query_text)),
                            model.articles_table.c.board_id == board.id,
                            not_(model.articles_table.c.is_searchable == False)))[offset:last].order_by(model.Article.id.desc()).all()
                else:
                    result = session.query(model.Article).join('author').filter(and_(or_(
                            model.articles_table.c.title.like(db_query_text),
                            model.articles_table.c.content.like(db_query_text),
                            model.User.username.like(db_query_text)),
                            not_(model.articles_table.c.is_searchable == False)))[offset:last].order_by(model.Article.id.desc()).all()
                end_time = time.time()
                search_dict_list = self._get_dict_list(result, SEARCH_ARTICLE_WHITELIST)
                ret_dict['hit'] = search_dict_list
                ret_dict['results'] = article_count
                ret_dict['search_time'] = str(end_time-start_time)
                ret_dict['last_page'] = last_page
                session.close()
                return True, ret_dict
        elif search_type.upper() == 'TITLE':
            start_time = time.time()
            article_count = session.query(model.Article).filter(and_(
                    model.articles_table.c.title.like(db_query_text),
                    model.articles_table.c.board_id == board.id,
                    not_(model.articles_table.c.is_searchable == False))).count()
            last_page = int(article_count / page_length)
            if article_count % page_length != 0:
                last_page += 1
            elif article_count == 0:
                last_page += 1
            if page > last_page:
                session.close()
                return False, 'WRONG_PAGENUM'
            offset = page_length * (page - 1)
            last = offset + page_length
            result = session.query(model.Article).filter(and_(
                    model.articles_table.c.title.like(db_query_text),
                    model.articles_table.c.board_id == board.id,
                    not_(model.articles_table.c.is_searchable == False)))[offset:last].order_by(model.Article.id.desc()).all()
            end_time = time.time()
            search_dict_list = self._get_dict_list(result, SEARCH_ARTICLE_WHITELIST)
            ret_dict['hit'] = search_dict_list
            ret_dict['results'] = article_count
            ret_dict['search_time'] = str(end_time-start_time)
            ret_dict['last_page'] = last_page
            session.close()
            return True, ret_dict
        elif search_type.upper() == 'CONTENT':
            start_time = time.time()
            article_count = session.query(model.Article).filter(and_(
                    model.articles_table.c.content.like(db_query_text),
                    model.articles_table.c.board_id == board.id,
                    not_(model.articles_table.c.is_searchable == False))).count()
            last_page = int(article_count / page_length)
            if article_count % page_length != 0:
                last_page += 1
            elif article_count == 0:
                last_page += 1
            if page > last_page:
                session.close()
                return False, 'WRONG_PAGENUM'
            offset = page_length * (page - 1)
            last = offset + page_length
            result = session.query(model.Article).filter(and_(
                    model.articles_table.c.content.like(db_query_text),
                    model.articles_table.c.board_id == board.id,
                    not_(model.articles_table.c.is_searchable == False)))[offset:last].order_by(model.Article.id.desc()).all()
            end_time = time.time()
            search_dict_list = self._get_dict_list(result, SEARCH_ARTICLE_WHITELIST)
            ret_dict['hit'] = search_dict_list
            ret_dict['results'] = article_count
            ret_dict['search_time'] = str(end_time-start_time)
            ret_dict['last_page'] = last_page
            session.close()
            return True, ret_dict
        elif search_type.upper() == 'AUTHOR_NICK':
            start_time = time.time()
            try:
                user = session.query(model.User).filter_by(nickname=query_text).one()
            except InvalidRequestError:
                session.close()
                return False, 'USER_NOT_EXIST'
            article_count = session.query(model.Article).filter(and_(
                    model.articles_table.c.author_id == user.id,
                    model.articles_table.c.board_id == board.id,
                    not_(model.articles_table.c.is_searchable == False))).count()
            last_page = int(article_count / page_length)
            if article_count % page_length != 0:
                last_page += 1
            elif article_count == 0:
                last_page += 1
            if page > last_page:
                session.close()
                return False, 'WRONG_PAGENUM'
            offset = page_length * (page - 1)
            last = offset + page_length
            result = session.query(model.Article).filter(and_(
                    model.articles_table.c.author_id == user.id,
                    model.articles_table.c.board_id == board.id,
                    not_(model.articles_table.c.is_searchable == False)))[offset:last].order_by(model.Article.id.desc()).all()
            end_time = time.time()
            search_dict_list = self._get_dict_list(result, SEARCH_ARTICLE_WHITELIST)
            ret_dict['hit'] = search_dict_list
            ret_dict['results'] = article_count
            ret_dict['search_time'] = str(end_time-start_time)
            ret_dict['last_page'] = last_page
            session.close()
            return True, ret_dict
        elif search_type.upper() == 'AUTHOR_USERNAME':
            start_time = time.time()
            try:
                user = session.query(model.User).filter_by(username=query_text).one()
            except InvalidRequestError:
                session.close()
                return False, 'USER_NOT_EXIST'
            article_count = session.query(model.Article).filter(and_(
                    model.articles_table.c.author_id == user.id,
                    model.articles_table.c.board_id == board.id,
                    not_(model.articles_table.c.is_searchable == False))).count()
            last_page = int(article_count / page_length)
            if article_count % page_length != 0:
                last_page += 1
            elif article_count == 0:
                last_page += 1
            if page > last_page:
                session.close()
                return False, 'WRONG_PAGENUM'
            offset = page_length * (page - 1)
            last = offset + page_length
            result = session.query(model.Article).filter(and_(
                    model.articles_table.c.author_id == user.id,
                    model.articles_table.c.board_id == board.id,
                    not_(model.articles_table.c.is_searchable == False)))[offset:last].order_by(model.Article.id.desc()).all()
            end_time = time.time()
            search_dict_list = self._get_dict_list(result, SEARCH_ARTICLE_WHITELIST)
            ret_dict['hit'] = search_dict_list
            ret_dict['results'] = article_count
            ret_dict['search_time'] = str(end_time-start_time)
            ret_dict['last_page'] = last_page
            session.close()
            return True, ret_dict
        elif search_type.upper() == 'DATE':
            session.close()
            return False, 'NOT_IMPLEMENTED'
        else:
            session.close()
            return False, 'WRONG_SEARCH_METHOD'
# vim: set et ts=8 sw=4 sts=4
