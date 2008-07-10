# -*- coding: utf-8 -*-
import datetime
import time

from arara.util import require_login

class NotLoggedIn(Exception):
    pass

class ArticleManager(object):
    '''
    게시글 및 검색 처리 클래스
    현재 게시글 표시방식이 절묘하기 때문에 read 메소드에 관한 논의가 필요.

    용법 : arara/test/article_manager.txt
    '''

    def __init__(self, login_manager):
        #monk data
        self.articles = {'garbages': {} }
        self.login_manager = login_manager
        self.article_no = 0

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

        try:
            board = self.articles[board_name]
        except KeyError:
            return False, 'BOARD_NOT_EXIST'

        try:
            article = board[no]
            return True, article
        except KeyError:
            return False, 'ARTICLE_NOT_EXIST'

    @require_login
    def write_article(self, session_key, board_name, article_dic):
        '''
        DB에 게시글 하나를 작성함
        Article Dictionary { no, read_status, title, content, author, date, hit, vote }

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

        try:
            board = self.articles[board_name]
        except KeyError:
            return False, 'BOARD_NOT_EXIST'

        import datetime

        ip = self.login_manager.get_session(session_key)[1]['ip']
        article_dic['ip'] = ip
        article_dic['time'] = str(datetime.datetime.fromtimestamp(time.time()))

        self.article_no += 1
        self.articles[board_name][self.article_no] = article_dic
        self.articles[board_name][self.article_no]['reply'] = []
        return True, self.article_no

    @require_login
    def write_reply(self, session_key, board_name, article_no, reply_dic):
        '''
        댓글 하나를 해당하는 글에 추가

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

        try:
            board = self.articles[board_name]
        except KeyError:
            return False, 'BOARD_NOT_EXIST'

        try:
            article = board[article_no]
            #reply_no = len(board[self.article_no]['reply']) + 1
            #board[self.article_no]['reply'][reply_no] = reply_dic
            ip = self.login_manager.get_session(session_key)[1]['ip']
            reply_dic['ip'] = ip
            reply_dic['time'] = str(datetime.datetime.fromtimestamp(time.time()))

            board[article_no]['reply'].append(reply_dic)
            return True, 'OK'
        except KeyError:
            return False, 'ARTICLE_NOT_EXIST'


    @require_login
    def modify(self, session_key, board_name, no, article_dic):
        '''
        DB의 해당하는 게시글 수정

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

        try:
            board = self.articles[board_name]
        except KeyError:
            return False, 'BOARD_NOT_EXIST'

        try:
            article = board[no]
            try:
                for key in article_dic:
                    board[no][key] = article_dic[key]
            except KeyError:
                return False, 'WRONG_DIC_TYPE'

        except KeyError:
            return False, 'ARTICLE_NOT_EXIST'

        return True, no


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
        
        try:
            board = self.articles[board_name]
        except KeyError:
            return False, 'BOARD_NOT_EXIST'

        try:
            article = board[no]
        except KeyError:
            return False, 'ARTICLE_NOT_EXIST'

        article['context'] = '삭제된 게시물입니다'
        return True, no
        

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
            for no in len(self.articles[board_name]):
                article_list.append(self.articles[board_name][no])
            return True, article_list 
        except KeyError: 
            return False, 'BOARD_NOT_EXIST'
             
    @require_login
    def board_list(self, session_key):
        '''
        게시판 목록 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, list
        @return:
            1. 리스트 읽어오기 성공: True, Dictionary of boards with new article num
            2. 리스트 읽어오기 실패: False 
                1. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        board = {}
        for boardname in self.articles:
            board[boardname] = len(self.articles[boardname])
        return True, board

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
        return False, 'NOT_IMPLEMENTED'

# vim: set et ts=8 sw=4 sts=4
