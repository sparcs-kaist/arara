# -*- coding: utf-8 -*-


from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy.sql import func, select
from arara.util import require_login
from arara import model
from arara.util import require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_important

log_method_call = log_method_call_with_source('read_status_manager')
log_method_call_important = log_method_call_with_source_important('read_status_manager')

class ReadStatus(object):
    def __init__(self, default='N'):
        self.default = default
        self.data = [(0, default)]

    def _find(self, n):
        '''적당한 터플을 찾는다'''
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

    def get(self, n):
        idx = self._find(n)
        return self.data[idx][1]

    def get_range(self, range_list):
        ret = []
        for i in range_list:
            ret.append(self.get(i))
        return ret

    def set_range(self, range_list, value):
        for i in range_list:
            self.set(i, value)
        return True

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
        self.read_status = {}

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _set_member_manager(self, member_manager):
        self.member_manager = member_manager

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
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

    def _check_article_exist(self, no_data):
        session = model.Session()
        top_article = session.query(model.Article).from_statement(
                select(
                    [model.articles_table],
                    select([func.max(model.articles_table.c.id)]).label('top_article_id')==model.articles_table.c.id)
                )[0]
        session.close()
        if type(no_data) == list:
            for no in no_data:
                if no > top_article.id:
                    
                    return False, 'ARTICLE_NOT_EXIST'
        else:
            if no_data > top_article.id:
                return False, 'ARTICLE_NOT_EXIST'
        return True, 'OK'

    def _initialize_data(self, user):
        session = model.Session()
        if not self.read_status.has_key(user.id):
            self.read_status[user.id] = {}
            read_status = session.query(model.ReadStatus).filter_by(user_id=user.id).all()
            read_status_dict_list = self._get_dict_list(read_status)
            session.close()
            if read_status_dict_list:
                for item in read_status_dict_list:
                    self.read_status[user.id] = item['read_status_data']
                return True, 'OK'
            else:
                status_dict = {}
                read_status_class = ReadStatus()
                status_dict = read_status_class
                self.read_status[user.id] = status_dict
                return True, 'OK'
        else:
            return False, 'ALREADY_ADDED'

    @require_login
    @log_method_call
    def check_stat(self, session_key, no):
        '''
        읽은 글인지의 여부를 체크

        >>> readstat.check_stat(session_key, 'garbages', 334)
        True, 'R'

        @type  session_key: string
        @param session_key: User Key
        @type  no: integer
        @param no: Article Number
        @rtype: string
        @return:
            1. 읽은글 여부 체크 성공:
                1. 이미 읽은 글: True, 'R'
                2. 읽지 않은 글: True, 'N'
                3. 읽지 않고 통과한 글: True, 'V'
            2. 읽은글 여부 체크 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        if ret:
            session = model.Session()
            user = session.query(model.User).filter_by(username=user_info['username']).one()
            session.close()
            ret, _ = self._initialize_data(user)
            ret, msg = self._check_article_exist(no)
            if ret:
                status = self.read_status[user.id].get(no)
                return True, status
            else:
                return ret, msg

    @require_login
    @log_method_call
    def check_stats(self, session_key, no_list):
        '''
        복수개의 글의 읽은 여부를 체크

        >>> readstat.check_stats(session_key, 'garbages', [1, 2, 3, 4, 5, 6])
        True, ['N', 'N', 'R', 'R', 'V', 'R']

        @type  session_key: string
        @param session_key: User Key
        @type  no_list: list
        @param no_list: Article Numbers
        @rtype: list
        @return:
            1. 읽은글 여부 체크 성공: True, read_stat_list
            2. 읽은글 여부 체크 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret, user_info = self.login_manager.get_session(session_key)
        if ret:
            session = model.Session()
            user = session.query(model.User).filter_by(username=user_info['username']).one()
            session.close()
            ret, _ = self._initialize_data(user)
            ret, msg = self._check_article_exist(no_list)
            if ret:
                status = self.read_status[user.id].get_range(no_list)
                return True, status
            else:
                return ret, msg

    @require_login
    @log_method_call
    def mark_as_read_list(self, session_key, no_list):
        '''
        읽은 글로 복수개의 글을 등록하기

        >>> readstat.mark_as_read(session_key, 'garbages', 34)
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
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
        ret, user_info = self.login_manager.get_session(session_key)
        if ret:
            session = model.Session()
            user = session.query(model.User).filter_by(username=user_info['username']).one()
            session.close()
            ret, _ = self._initialize_data(user)
            ret, msg = self._check_article_exist(no_list)
            if ret:
                status = self.read_status[user.id].set_range(no_list, 'R')
                return True, 'OK'
            else:
                return ret, msg

    @require_login
    @log_method_call
    def mark_as_read(self, session_key, no):
        '''
        읽은 글로 등록하기

        >>> readstat.mark_as_read(session_key, 'garbages', 34)
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
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
        ret, user_info = self.login_manager.get_session(session_key)
        if ret:
            session = model.Session()
            user = session.query(model.User).filter_by(username=user_info['username']).one()
            session.close()
            ret, _ = self._initialize_data(user)
            ret, msg = self._check_article_exist(no)
            if ret:
                status = self.read_status[user.id].set(no, 'R')
                return True, 'OK'
            else:
                return ret, msg

    @require_login
    @log_method_call
    def mark_as_viewed(self, session_key, no):
        '''
        통과한 글로 등록하기

        @type  session_key: string
        @param session_key: User Key
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
        ret, user_info = self.login_manager.get_session(session_key)
        if ret:
            session = model.Session()
            user = session.query(model.User).filter_by(username=user_info['username']).one()
            session.close()
            ret, _ = self._initialize_data(user)
            ret, msg = self._check_article_exist(no)
            if ret:
                status = self.read_status[user.id].set(no, 'V')
                return True, 'OK'
            else:
                return ret, msg

    @log_method_call
    def save_to_database(self, user_id=None, session_key=None):
        if user_id:
            pass
        elif session_key:
            ret, user_info = self.login_manager.get_session(session_key)
            if ret:
                pass
            else:
                return False, 'NOT_LOGGEDIN'
        else:
            return False, 'WRONG_REQUEST'


# vim: set et ts=8 sw=4 sts=4
