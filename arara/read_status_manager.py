# -*- coding: utf-8 -*-
import logging

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy.sql import func, select
from arara.util import require_login
from arara import model
from arara.util import require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_duration, log_method_call_with_source_important
from arara.util import smart_unicode

from arara_thrift.ttypes import *

log_method_call = log_method_call_with_source('read_status_manager')
log_method_call_duration = log_method_call_with_source_duration('read_status_manager')
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

    def __repr__(self):
        printed_str = ""
        for item in self.data:
            printed_str += str(item)
        return printed_str

class ReadStatusManager(object):
    '''
    읽은 글, 통과한글 처리관련 클래스
    '''

    def __init__(self, engine):
        self.engine = engine
        self.read_status = {}
        self.logger = logging.getLogger('read_status_manager')

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
        # 함수의 내용이 ArticleManager 로 옮겨갔다. 
        self.engine.article_manager.check_article_exist(no_data)

    def _initialize_data(self, user_id):
        if not self.read_status.has_key(user_id):
            try:
                session = model.Session()
                read_status = session.query(model.ReadStatus).filter_by(user_id=user_id).one()
                self.read_status[user_id] = read_status.read_status_data
                session.close()
                return True, 'OK'
            except InvalidRequestError:
                self.read_status[user_id] = ReadStatus()
                session.close()
                return True, 'OK'
        else:
            return False, 'ALREADY_ADDED'

    def _check_stat(self, user_id, no):
        '''
        읽은 글인지의 여부를 체크. 로그 따로 남기지 않음.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        @type  no: integer
        @param no: Article Number
        @rtype: string
        @return:
            1. 읽은글 여부 체크 성공:
                1. 이미 읽은 글: 'R'
                2. 읽지 않은 글: 'N'
                3. 읽지 않고 통과한 글: 'V' <- 정말 이럴까?
            2. 읽은글 여부 체크 실패:
                1. 데이터베이스 오류: InternalError('DATABASE_ERROR') <- 정말 이럴까?
        '''
        ret, _ = self._initialize_data(user_id)
        self._check_article_exist(no)
        status = self.read_status[user_id].get(no)
        return status

    @require_login
    @log_method_call
    def check_stat(self, session_key, no):
        '''
        읽은 글인지의 여부를 체크

        >>> readstat.check_stat(session_key, 334)
        'R'

        @type  session_key: string
        @param session_key: User Key
        @type  no: integer
        @param no: Article Number
        @rtype: string
        @return:
            1. 읽은글 여부 체크 성공:
                1. 이미 읽은 글: 'R'
                2. 읽지 않은 글: 'N'
                3. 읽지 않고 통과한 글: 'V' <- ... 정말?
            2. 읽은글 여부 체크 실패:
                1. 로그인되지 않은 유저: NotLoggedIn()
                2. 데이터베이스 오류: InternalError('DATABASE_ERROR') <- 정말?
        '''
        # TODO: require_login 이 하는 일을 get_user_id 가 이미 하지 않는가?
        user_id = self.engine.login_manager.get_user_id(session_key)
        return self._check_stat(user_id, no)

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
        user_id = self.engine.login_manager.get_user_id(session_key)
        ret, _ = self._initialize_data(user_id)
        self._check_article_exist(no_list)
        status = self.read_status[user_id].get_range(no_list)
        return status

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
        user_id = self.engine.login_manager.get_user_id(session_key)
        ret, _ = self._initialize_data(user_id)
        self._check_article_exist(no_list)
        status = self.read_status[user_id].set_range(no_list, 'R')

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
        user_id = self.engine.login_manager.get_user_id(session_key)
        ret, _ = self._initialize_data(user_id)
        self._check_article_exist(no)
        status = self.read_status[user_id].set(no, 'R')

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
        user_id = self.engine.login_manager.get_user_id(session_key)
        ret, _ = self._initialize_data(user_id)
        self._check_article_exist(no)
        status = self.read_status[user_id].set(no, 'V')

    @log_method_call
    @log_method_call_duration
    def save_to_database(self, username):
        import traceback
        session = model.Session()
        user = self.engine.member_manager._get_user(session, username)
        if self.read_status.has_key(user.id):
            # Memory 에 확실히 있음
            try:
                read_stat = session.query(model.ReadStatus).filter_by(user_id=user.id).one()
                read_stat.read_status_data = self.read_status[user.id]
                session.commit()
                id = user.id
                del self.read_status[id]
            except KeyError:
                # 메모리에서 중간에 날아갔거나 한 경우
                # 별 문제는 없다
                pass
            except InvalidRequestError:
                # DB 에 확실히 없는 경우
                # 이 때는 새롭게 생성해 줘야 한다
                try:
                    new_read_stat = model.ReadStatus(user, self.read_status[user.id])
                    session.add(new_read_stat)
                    session.commit()
                    id = user.id
                    del self.read_status[id]
                except KeyError:
                    # 아마도 이 경우에는 초고속으로 동일사용자를 2회 로그아웃해서
                    # del self.read_status[id] 가 들어가는 동안 같은 곳에 위치했는지도.
                    pass
            except Exception:
                # ReadStatus 관련 에러 발생
                logging.error(traceback.format_exc())
        # Memory 에 없는 경우는 그냥 잊어버린다.

        # 어쨌뜬 세션을 닫는다.
        session.close()

# vim: set et ts=8 sw=4 sts=4
