# -*- coding: utf-8 -*-
import logging
import traceback

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy.sql import func, select

from arara import model
from arara.util import require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_duration, log_method_call_with_source_important
from arara.read_status import ReadStatus
from arara.read_status.default_backend import ReadStatusManagerDefault

from arara_thrift.ttypes import *

log_method_call = log_method_call_with_source('read_status_manager_db')
log_method_call_duration = log_method_call_with_source_duration('read_status_manager_db')
log_method_call_important = log_method_call_with_source_important('read_status_manager_db')

class ReadStatusManagerDB(ReadStatusManagerDefault):
    '''
    읽은 글, 통과한글 처리관련 클래스
    '''

    def __init__(self, engine):
        super(ReadStatusManagerDB, self).__init__(engine)
        self.read_status = {}

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

    def _initialize_data(self, user_id):
        if not user_id in self.read_status:
            try:
                session = model.Session()
                read_status = session.query(model.ReadStatus).filter_by(user_id=user_id).one()
                if read_status.read_status_numbers == None:
                    self.read_status[user_id] = read_status.read_status_data
                else:
                    self.read_status[user_id] = ReadStatus.from_string(read_status.read_status_numbers, read_status.read_status_markers)
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
                3. 읽지 않고 통과한 글: 'V' <- 정말 이럴까?
            2. 읽은글 여부 체크 실패:
                1. 데이터베이스 오류: InternalError('DATABASE_ERROR') <- 정말 이럴까?
        '''
        ret, _ = self._initialize_data(user_id)
        status = self.read_status[user_id].get(no)
        return status

    @require_login
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
                3. 읽지 않고 통과한 글: 'V' <- ... 정말?
            2. 읽은글 여부 체크 실패:
                1. 로그인되지 않은 유저: NotLoggedIn()
                2. 데이터베이스 오류: InternalError('DATABASE_ERROR') <- 정말?
        '''
        # TODO: require_login 이 하는 일을 get_user_id 가 이미 하지 않는가?
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
        self._initialize_data(user_id)
        return self.read_status[user_id].get_range(no_list)

    @require_login
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
        ret, _ = self._initialize_data(user_id)
        status = self.read_status[user_id].get_range(no_list)
        return status

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
        ret, _ = self._initialize_data(user_id)
        status = self.read_status[user_id].set_range(no_list, 'R')

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
        ret, _ = self._initialize_data(user_id)
        status = self.read_status[user_id].set(no, 'R')

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

    @require_login
    @log_method_call
    def mark_as_viewed(self, session_key, no):
        '''
        통과한 글로 등록하기
        존재하지 않는 글번호를 입력하지 않도록 주의.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  no: int
        @param no: Article Number
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
        status = self.read_status[user_id].set(no, 'V')

    @log_method_call_duration
    def _save_to_database(self, session, user_id):
        '''
        사용자의 ReadStatus 정보를 주어진 SQLAlchemy Session 에 기록한다.
        익셉션이 발생할 경우 Exception 은 raise 하나 session 은 닫지 않는다.
        session 처리는 전적으로 caller 의 몫이다.

        @type  session: model.Session
        @param session: SQLAlchemy Session
        @type  user_id: int
        @param user_id: 사용자 고유 id
        '''
        read_stat = None
        if user_id in self.read_status:
            # Memory 에 있는 경우
            try:
                read_stat = session.query(model.ReadStatus).filter_by(user_id=user_id).one()

                read_stat.read_status_data = None
                numbers, markers = self.read_status[user_id].to_string()
                read_stat.read_status_numbers = numbers
                read_stat.read_status_markers = markers

                self.logger.info("User id %d's ReadStatus is successfully saved.", user_id)

                del self.read_status[user_id]
            except KeyError:
                # 메모리에 key 가 없다면 별 문제는 없다.
                pass
            except InvalidRequestError:
                # DB 에 기록된 적이 없으므로 생성해야 한다.
                try:
                    user = self.engine.member_manager._get_user_by_id(session, user_id, False)
                    new_read_stat = model.ReadStatus(user, self.read_status[user_id])

                    new_read_stat.read_status_data = None
                    numbers, markers = self.read_status[user_id].to_string()
                    new_read_stat.read_status_numbers = numbers
                    new_read_stat.read_status_markers = markers
                    session.add(new_read_stat)
                    self.logger.info("User id %d's ReadStatus is successfully created.", user_id)

                    del self.read_status[user_id]
                except KeyError:
                    # 아마도 이 경우에는 초고속으로 동일사용자를 2회 로그아웃해서
                    # del self.read_status[id] 가 들어가는 동안 같은 곳에 위치했는지도.
                    pass
        # Proxy Object 를 유지시켜서 일으킨 변화가 반영되는지 보자
        return read_stat

    def save_to_database(self, user_id):
        '''
        메모리에 존재하는 특정 사용자의 ReadStatus 를 DB 에 기록하고 메모리에서 지운다.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        '''
        session = model.Session()
        try:
            result = self._save_to_database(session, user_id)
            session.commit()
            session.close()
        except Exception:
            logging.error(traceback.format_exc())
            session.close()

    @log_method_call_duration
    def _save_all_users_to_database(self):
        '''
        메모리에 존재하는 모든 사용자의 ReadStatus 를 DB 에 기록하고 메모리에서 지운다.
        '''
        session = model.Session()
        list_of_user_id = self.read_status.keys()
        list_of_proxies = [None] * len(list_of_user_id)

        for idx, user_id in enumerate(list_of_user_id):
            try:
                list_of_proxies[idx] = self._save_to_database(session, user_id)
            except Exception:
                logging.error(traceback.format_exc())

        # 어쨌뜬 세션을 닫는다.
        session.commit()
        session.close()

    @log_method_call_duration
    def save_users_read_status_to_database(self, user_ids):
        '''
        주어진 사용자들에 대한 ReadStatus 를 DB 에 기록하고 메모리에서 지운다.

        @type  user_ids: list<int>
        @param user_ids: ReadStatus 를 기록할 사용자들의 고유 id
        '''
        session = model.Session()
        try:
            for user_id in user_ids:
                try:
                    self._save_to_database(session, user_id)
                except Exception:
                    logging.error(traceback.format_exc())
            session.commit()
            session.close()
        except Exception:
            logging.error(traceback.format_exc())
            session.close()

    @log_method_call_duration
    def get_read_status_loaded_users(self):
        '''
        현재 ReadStatus 정보를 Memory에 들고 있는 사용자의 목록을 구한다.

        @rtype: list<int>
        @return: 사용자 고유 id 의 목록
        '''

        return self.read_status.keys()

    __public__ = [
            check_stat,
            check_stats,
            check_stats_by_id,
            mark_as_read_list,
            mark_as_read,
            mark_as_viewed,
            save_to_database,
            save_users_read_status_to_database,
            get_read_status_loaded_users]
