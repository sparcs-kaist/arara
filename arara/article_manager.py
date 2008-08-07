# -*- coding: utf-8 -*-
import datetime
import time
import xmlrpclib

from arara.util import require_login, filter_dict
from arara import model
from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import and_, or_, not_

WRITE_ARTICLE_DICT = ('title', 'content')
READ_ARTICLE_WHITELIST = ('id', 'title', 'content', 'last_modified_date', 'deleted', 'blacklisted', 'author_username', 'vote', 'date', 'hit', 'depth', 'root_id', 'is_searchable')
LIST_ARTICLE_WHITELIST = ('id', 'title', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'vote', 'hit', 'last_page')
BEST_ARTICLE_WHITELIST = ('id', 'title', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'vote', 'hit', 'last_page', 'board_name')

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
                stack.append((child, depth+1))
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
            return True, weekly_best_article_dict_list

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        session = model.Session()
        if item_dict.has_key('author_id'):
            item_dict['author_username'] = item.author.username
            del item_dict['author_id']
        if item_dict.has_key('board_id'):
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
        if item_dict.has_key('root_id'):
            if not item_dict['root_id']:
                item_dict['root_id'] = item_dict['id']
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(filtered_dict)
        return return_list

    def get_today_best_list(self, count=5):
        '''
        투베를 가져오는 함수

        @type  count: integer
        @param count: Number of today's best articles to get
        @rtype: list
        @return:
            1. 투베를 가져오는데 성공: True, Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        session = model.Session()
        ret, today_best_list = self._get_today_best_article(None, None, count)
        if ret:
            return True, today_best_list
        else:
            return False, 'DATABASE_ERROR'

    def get_weekly_best_list(self, count=5):
        '''
        윅베를 가져오는 함수

        @type  count: integer
        @param count: Number of today's best articles to get
        @rtype: list
        @return:
            1. 투베를 가져오는데 성공: True, Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        session = model.Session()
        ret, weekly_best_list = self._get_weekly_best_article(None, None, count)
        if ret:
            return True, weekly_best_list
        else:
            return False, 'DATABASE_ERROR'

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
        article_list = []
        try:
            session = model.Session()
            ret, _ = self._is_board_exist(board_name)
            if ret:
                board = session.query(model.Board).filter_by(board_name=board_name).one()
                article_count = session.query(model.Article).filter_by(board_id=board.id, root_id=None).count()
                page_length -= 2
                last_page = int(article_count / page_length)
                if article_count % page_length != 0:
                    last_page += 1
                elif article_count == 0:
                    last_page += 1
                if page > last_page:
                    return False, 'WRONG_PAGENUM'
                offset = page_length * (page - 1)
                last = offset + page_length
                article_list = session.query(model.Article).filter_by(board_id=board.id, root_id=None)[offset:last].order_by(model.Article.id.desc()).all()
                article_dict_list = self._get_dict_list(article_list, LIST_ARTICLE_WHITELIST)
                ret, weekly_best_article_dict_list = self._get_weekly_best_article(session_key, board, 1)
                ret, today_best_article_dict_list = self._get_today_best_article(session_key, board, 1)
                if weekly_best_article_dict_list:
                    article_dict_list.insert(0, weekly_best_article_dict_list[0])
                if today_best_article_dict_list:
                    article_dict_list.insert(0, today_best_article_dict_list[0])
                article_dict_list.append({'last_page': last_page})
                for article in article_dict_list:
                    if article.has_key('id'):
                        if not article.has_key('type'):
                            article['type'] = 'normal'
                        ret, msg = self.read_status_manager.check_stat(session_key, board_name, article['id'])
                        if ret:
                            article['read_status'] = msg
                return True, article_dict_list
            else:
                return ret, 'BOARD_NOT_EXIST'
        except InvalidRequestError:
            raise
            return False, 'DATABASE_ERROR'
             
    @require_login
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
                return False, 'ARTICLE_NOT_EXIST'
            article_dict_list = self._article_thread_to_list(article)
            for item in article_dict_list:
                if item['author_username'] in blacklist_users:
                    item['blacklisted'] = True
                else:
                    item['blacklisted'] = False
                ret, msg = self.read_status_manager.mark_as_read(session_key, board_name, item['id'])
                if not ret:
                    return ret, msg
            return True, article_dict_list
        else:
            return ret, message

    @require_login
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
                return False, 'ARTICLE_NOT_EXIST'
            user = session.query(model.User).filter_by(username=user_info['username']).one()
            vote_unique_check = session.query(model.ArticleVoteStatus).filter_by(user_id=user.id, board_id=board.id, article_id = article.id).all()
            if vote_unique_check:
                return False, 'ALREADY_VOTED'
            else:
                article.vote += 1
                vote = model.ArticleVoteStatus(user, board, article)
                session.save(vote)
                session.commit()
                return True, 'OK'

    @require_login
    def write_article(self, session_key, board_name, article_dic):
        '''
        DB에 게시글 하나를 작성함

        Article Dictionary { title, content, is_searchable, attach1, attach2 }
        attach1, attach2는 아직 구현되지 않음

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
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        ret, message = self._is_board_exist(board_name)
        if ret:
            session = model.Session()
            author = session.query(model.User).filter_by(username=user_info['username']).one()
            board = session.query(model.Board).filter_by(board_name=board_name).one()
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
        else:
            return ret, message
        return True, new_article.id

    @require_login
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
            except InvalidRequestError:
                return False, 'ARTICLE_NOT_EXIST'
        else:
            return ret, message
        return True, new_reply.id

    @require_login
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
                    return False, "NO_PERMISSION"
                if article.author_id == author.id:
                    article.title = article_dic['title']
                    article.content = article_dic['content']
                    article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
                    session.commit()
                else:
                    return False, "NO_PERMISSION"
            except InvalidRequestError:
                return False, "ARTICLE_NOT_EXIST"
        else:
            return ret, message
        return True, article.id

    @require_login
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
                else:
                    return False, "NO_PERMISSION"
            except InvalidRequestError:
                return False, "ARTICLE_NOT_EXIST"
        else:
            return ret, message
        return True, article.id
        
    @require_login
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
    def search(self, session_key, board_name, query_text, search_type, page=1, page_length=20):
        '''
        게시물 검색

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: BBS Name
        @type  query_text: string
        @param query_text: Text to Search
        @type  search_type: string
        @param search_type: Search Type (Title, Context, Author, Date, All)
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
        ret = self._is_board_exist(board_name)
        if not ret:
            return False, 'BOARD_NOT_EXIST'
        search_manager = xmlrpclib.Server('http://nan.sparcs.org:9000/api')
        query = str(query_text) + ' source:ara'
        result = search_manager.search('00000000000000000000000000000000',query)
        return True, result

# vim: set et ts=8 sw=4 sts=4
