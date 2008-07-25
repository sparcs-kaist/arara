# -*- coding: utf-8 -*-

from arara.util import require_login

class ReadStatus(object):
    def __init__(self):
        self.default = 'N'
        self.data = [(0, 'N'), (15, 'R'), (20, 'V'), (25, 'N')]

    def _search(self, value, data_to_search, start=0, large=-1):
        #TODO: NOT COMPLETED, NEED TO COMPLETE AND CHECK IF THIS WORKS
        if start == 0:
            half = int(len(data_to_search) / 2)
        else:
            if large == 1:
                half = start + int(len(data_to_search[start:]) / 2)
            elif large == 0:
                half = start - int(len(data_to_search[0:start]) / 2)
        no, data = data_to_search[half]

        print half, start
        print no, data
        if half == start:
            return no, data

        if value > no:
            self._search(value, data_to_search, half, 1)
        elif value < no:
            self._search(value, data_to_search, half, 0)
        else:
            return no, data
        #TODO: NOT COMPLETED, NEED TO COMPLETE AND CHECK IF THIS WORKS

    def get_data(self, article_no):
        if article_no < 0:
            return False, 'WRONG_ARTICLE_NO'
        for no, status in self.data:
            if article_no > no:
                ret_status = status
            elif article_no < no:
                return ret_status
        return ret_status

    def set_data(self, article_no, status):
        for index, (no, data_status) in enumerate(self.data):
            if article_no > no:
                left = self.data[index-1]
                right = self.data[index+1]
                if article_no < right[0]:
                    if self.data[index+1][0] == article_no + 1:
                        if self.data[index+1][1] == status:
                            del self.data[index+1]
                            self.data.insert(index+1, (article_no, status))
                            return True, 'OK'
                    else:
                        self.data.insert(index+1, (article_no+1, data_status))
                        self.data.insert(index+1, (article_no, status))
                        return True, 'OK'
                else:
                    if self.data[index][0] == article_no - 1:
                        print 2
                        if not self.data[index][1] == status:
                            print 3
                            self.data.append((article_no, status))
                            return True, 'OK'


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
