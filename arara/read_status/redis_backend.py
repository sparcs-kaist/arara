# -*- coding: utf-8 -*-
import logging
import traceback
import redis
from redis.exceptions import ConnectionError

from arara.util import require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_duration, log_method_call_with_source_important
from arara.read_status.default_backend import ReadStatusManagerDefault
from etc import arara_settings

log_method_call = log_method_call_with_source('read_status_manager_redis')
log_method_call_duration = log_method_call_with_source_duration('read_status_manager_redis')
log_method_call_important = log_method_call_with_source_important('read_status_manager_redis')

class ReadStatusManagerRedis(ReadStatusManagerDefault):
    '''
    읽은 글, 통과한글 처리관련 클래스
    '''

    def __init__(self, engine):
        super(ReadStatusManagerRedis, self).__init__(engine)
        # r_check DB
        # DB No: 1
        # Key: user_id + '_' + no, value: 
        # Value: 'R' or 'V' ( readed, checked )
        self.r_check = redis.StrictRedis(host='127.0.0.1', port=arara_settings.REDIS_PORT, db=1)
        # r_user DB
        # DB No: 0
        # Key: user_id
        # Value: list of read articles
        self.r_user = redis.StrictRedis(host='127.0.0.1', port=arara_settings.REDIS_PORT, db=0)

    def _make_key(self, user_id, no):
        return str(user_id) + '_' + str(no)

    def _check_stat(self, user_id, no):
        '''
        읽은 글인지의 여부를 체크. 로그 따로 남기지 않음.
        존재하지 않는 글번호를 입력하지 않도록 주의.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        @type  no: int
        @param no: Article Number
        @rtype: string
        @return:
            1. 읽은글 여부 체크 성공:
                1. 이미 읽은 글: 'R'
                2. 읽지 않은 글: 'N'
                3. 읽지 않고 통과한 글: 'V' <- Not supported
            2. 읽은글 여부 체크 실패:
                1. 데이터베이스 오류: InternalError('DATABASE_ERROR')
        '''
        try:
            if self.r_check.sismember(user_id, no):
                return 'R'
            else:
                return 'N'
        except ConnectionError:
            raise InternalError('DATABASE_ERROR')

    @log_method_call
    def check_stat(self, session_key, no):
        '''
        읽은 글인지의 여부를 체크
        존재하지 않는 글번호를 입력하지 않도록 주의.

        >>> readstat.check_stat(session_key, 334)
        'R'

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  no: int
        @param no: Article Number
        @rtype: string
        @return:
            1. 읽은글 여부 체크 성공:
                1. 이미 읽은 글: 'R'
                2. 읽지 않은 글: 'N'
                3. 읽지 않고 통과한 글: 'V' <- Not supported
            2. 읽은글 여부 체크 실패:
                1. 로그인되지 않은 유저: NotLoggedIn()
                2. 데이터베이스 오류: InternalError('DATABASE_ERROR')
        '''
        user_id = self.engine.login_manager.get_user_id(session_key)
        return self._check_stat(user_id, no)

    @log_method_call
    def check_stats_by_id(self, user_id, no_list):
        '''
        사용자 고유 id 를 받아 복수개의 글의 읽은 여부를 체크
        존재하지 않는 글번호를 입력하지 않도록 주의.

        >>> readstat.check_stats(session_key, [1, 2, 3, 4, 5, 6])
        ['N', 'N', 'R', 'R', 'V', 'R']

        @type  no_list: list<int>
        @param no_list: Article Numbers
        @rtype: list<str>
        @return: 주어진 각 게시물별 글읽음 상태
        '''
        pipe = self.r_check.pipeline()
        for n in no_list:
            pipe.sismember(user_id, n)

        try:
            result = pipe.execute()
        except ConnectionError:
            raise InternalError('DATABASE_ERROR')

        return [x and 'R' or 'N' for x in result]

    @log_method_call
    def check_stats(self, session_key, no_list):
        '''
        복수개의 글의 읽은 여부를 체크
        존재하지 않는 글번호를 입력하지 않도록 주의.

        >>> readstat.check_stats(session_key, 'garbages', [1, 2, 3, 4, 5, 6])
        True, ['N', 'N', 'R', 'R', 'V', 'R']

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  no_list: list<int>
        @param no_list: Article Numbers
        @rtype: list<string>
        @return:
            1. 읽은글 여부 체크 성공: read_stat_list
            2. 읽은글 여부 체크 실패:
                1. 로그인되지 않은 유저: NotLoggedIn
                2. 데이터베이스 오류: InternalError('DATABASE_ERROR')
        '''
        user_id = self.engine.login_manager.get_user_id(session_key)
        return self.check_stats_by_id(user_id, no_list)

    @log_method_call
    def _mark_as_read_list(self, user_id, no_list):
        '''
        복수개의 글을 읽은 글로 등록하기
        존재하지 않는 글번호를 입력하지 않도록 주의.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        @type  no_list: list<int>
        @param no_list: 글번호 목록
        @rtype: void
        @return:
            1. 등록 성공: void
            2. 등록 실패:
                1. 존재하지 않는 글: InvalidOperation('ARTICLE_NOT_EXIST')
                2. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR')
        '''
        pipe = self.r_check.pipeline()
        for n in no_list:
            pipe.sadd(user_id, n)

        try:
            result = pipe.execute()
        except ConnectionError:
            raise InternalError('DATABASE_ERROR')

    @require_login
    @log_method_call
    def mark_as_read_list(self, session_key, no_list):
        '''
        복수개의 글을 읽은 글로 등록하기
        존재하지 않는 글번호를 입력하지 않도록 주의.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  no_list : list<int>
        @param no_list : 글번호 목록
        @rtype: void
        @return:
            1. 등록 성공: void
            2. 등록 실패:
                1. 존재하지 않는 글: InvalidOperation('ARTICLE_NOT_EXIST')
                2. 로그인되지 않은 유저: NotLoggedIn
                3. 데이터베이스 오류: InternalError('DATABASE_ERROR')
        '''
        user_id = self.engine.login_manager.get_user_id(session_key)
        self._mark_as_read_list(user_id, no_list)

    @log_method_call_duration
    def _mark_as_read(self, user_id, no):
        '''
        읽은 글로 등록하기
        존재하지 않는 글번호를 입력하지 않도록 주의.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        @type  no: int
        @param no: Article Number
        @return:
            1. 등록 성공: void
            2. 등록 실패:
                1. 존재하지 않는 글: InvalidOperation('ARTICLE_NOT_EXIST')
                2. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR')
        '''
        try:
            self.r_check.sadd(user_id, no)
        except ConnectionError:
            raise InternalError('DATABASE_ERROR')

    @require_login
    @log_method_call
    def mark_as_read(self, session_key, no):
        '''
        읽은 글로 등록하기
        존재하지 않는 글번호를 입력하지 않도록 주의.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  no: int
        @param no: Article Number
        @rtype: void
        @return:
            1. 등록 성공: void
            2. 등록 실패:
                1. 존재하지 않는 글: InvalidOperation('ARTICLE_NOT_EXIST')
                2. 로그인되지 않은 유저: NotLoggedIn
                3. 데이터베이스 오류: InternalError('DATABASE_ERROR')
        '''
        user_id = self.engine.login_manager.get_user_id(session_key)
        self._mark_as_read(user_id, no)

    def _save_all_users_to_database(self):
        self.r_check.save()
        self.r_user.save()

#    __public__ = []
