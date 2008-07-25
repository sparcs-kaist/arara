# -*- coding: utf-8 -*-

from arara.util import require_login

class ReadStatus(object):
    def __init__(self, default='N'):
        self.default = default
        self.data = [(0, default)]

    def _rec_find(self, n):
        low = 0
        high = len(self.data) - 1
        while True:
            middle = (high - low) / 2 + low
            assert low <= middle <= high
            if self.data[middle][0] <= n:
                try:
                    if n < self.data[middle+1][0]:
                        return middle
                except IndexError:
                    return middle
            if self.data[middle][0] <= n:
                low = middle + 1
            else:
                high = middle - 1

    def _find(self, n):
        '''적당한 터플을 찾는다'''
        #return self._rec_find(n)
        for i, (lower_bound, value) in reversed(list(enumerate(self.data))):
            if lower_bound <= n:
                return i
        assert False

    def get(self, n):
        idx = self._find(n)
        return self.data[idx][1]

    def get_range(self, lower_bound, upper_bound):
        ret = []
        for i in range(lower_bound, upper_bound + 1):
            ret.append(self.get(i))
        return ret

    def _merge_right(self, idx):
        if self.data[idx][1] == self.data[idx + 1][1]:
            del self.data[idx + 1]

    def _merge_left(self, idx):
        self._merge_right(idx - 1)

    def _merge(self, idx):
        #print idx
        if idx == 0:
            self._merge_right(idx)
        elif idx == len(self.data) - 1:
            self._merge_left(idx)
        else:
            self._merge_right(idx)
            self._merge_left(idx)

    def set(self, n, value):
        found_idx = self._find(n)
        found_lower_bound = self.data[found_idx][0]
        found_value = self.data[found_idx][1]
        if found_value == value: return

        # 맨 앞일경우
        if n == 0:
            self.data[0] = (0, value)
            if len(self.data) == 1:
                self.data.append((1, self.default))
                self._merge(0)
            elif self.data[1][0] != 1:
                self.data.insert(1, (1, self.default))
                self._merge(1)
            return

        if found_lower_bound == n:
            self.data[found_idx] = (n, value)
            if len(self.data) == found_idx + 1:
                self.data.append((n + 1, self.default))
            elif self.data[found_idx + 1][0] != n + 1:
                assert self.data[found_idx + 1][0] != n
                self.data.insert(found_idx + 1, (n + 1, self.default))
                self._merge(found_idx)
            self._merge(found_idx - 1)
            return

        # 찾은 터플의 값이 셋팅 하려는 값과 다르므로 새로 맹근다.
        self.data.insert(found_idx + 1, (n, value))
        if len(self.data) == found_idx + 2:
            self.data.append((n + 1, self.default))
        elif self.data[found_idx + 2][0] != n + 1:
            self.data.insert(found_idx + 2, (n+1, self.default))
        self._merge(found_idx)
        self._merge(found_idx + 1)


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
