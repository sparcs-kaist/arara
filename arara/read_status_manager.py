# -*- coding: utf-8 -*-

from arara.util import require_login

class ReadStatusManager(object):
    '''
    읽은 글, 통과한글 처리관련 클래스
    '''

    def __init__(self):
        self.articles = {'garbages' : {1:{'read_status':'R'}, 2:{'read_status':'V'}}}
        
    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _set_member_manager(self, member_manager):
        self.member_manager = member_manager

    @require_login
    def check_stat(self, session_key, board_name, no):
        '''
        읽은 글인지의 여부를 체크

        >>> readstat.check_stat(session_key, 'garbages', 334)
        True, 'R'

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: board Name
        @type  no: integer
        @param no: Article Number
        @rtype: string
        @return:
            1. 읽은글 여부 체크 성공:
                1. 이미 읽은 글: True, 'R'
                2. 읽지 않은 글: True, 'N'
                3. 읽지 않고 통과한 글: True, 'V'
            2. 읽은글 여부 체크 실패:
                1. 존재하지 않는 글: False, 'ARTICLE_NOT_EXIST'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        try:
            board = self.articles[board_name]
            status = self.articles[board_name][no]['read_status'] 
            return True, status
        except KeyError:
            return False, 'ARTICLE_NOT_EXIST'

    @require_login
    def check_stats(self, session_key, board_name, no_list):
        '''
        복수개의 글의 읽은 여부를 체크

        >>> readstat.check_stats(session_key, 'garbages', [1, 2, 3, 4, 5, 6])
        True, ['N', 'N', 'R', 'R', 'V', 'R']

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: board Name
        @type  no_list: list
        @param no_list: Article Numbers
        @rtype: list
        @return:
            1. 읽은글 여부 체크 성공: True, read_stat_list
            2. 읽은글 여부 체크 실패:
                1. 존재하지 않는 글: False, 'ARTICLE_NOT_EXIST'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        try:
            board = self.articles[board_name]
            status = []
            for index in no_list:
                status.append(self.articles[board_name][index]['read_status']) 
            return True, status
        except KeyError:
            return False, 'ARTICLE_NOT_EXIST'



    @require_login
    def mark_as_read(self, session_key, board_name, no):
        '''
        읽은 글로 등록하기

        >>> readstat.mark_as_read(session_key, 'garbages', 34)
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: board Name
        @type  no : integer
        @param no : Article Number
        @rtype: string
        @return:
            1. 등록 성공: True, 'OK'
            2. 등록 실패:
                1. 존재하지 않는 글: False, 'ARTICLE_NOT_EXIST'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        try:
            board = self.articles[board_name]
            self.articles[board_name][no]['read_status'] = 'R' 
            return True, 'OK'
        except KeyError:
            return False, 'ARTICLE_NOT_EXIST'

    @require_login
    def mark_as_viewed(self, session_key, board_name, no):
        '''
        통과한 글로 등록하기

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: board Name
        @type  no : integer
        @param no : Article Number
        @rtype: string
        @return:
            1. 등록 성공: True, 'OK'
            2. 등록 실패:
                1. 존재하지 않는 글: False, 'ARTICLE_NOT_EXIST'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        try:
            board = self.articles[board_name]
            self.articles[board_name][no]['read_status'] = 'V' 
            return True, 'OK'
        except KeyError:
            return False, 'ARTICLE_NOT_EXIST'

# vim: set et ts=8 sw=4 sts=4
