# -*- coding: utf-8 -*-

from arara import arara_manager
from arara_thrift.ttypes import *

class ReadStatusManagerDefault(arara_manager.ARAraManager):
    '''
    읽은 글, 통과한글 처리관련 클래스. 실제로 아무 행동도 하지 않으며, 어떻게 자료를 저장하는가에 따라 이 클래스를 상속한 클래스를 사용한다. 다만 Setting에서 Store Type을 'none'으로 지정한 경우 이 클래스를 사용한다.
    '''

    def __init__(self, engine):
        super(ReadStatusManagerDefault, self).__init__(engine)

    def _check_stat(self, user_id, no):
        return 'N'

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
        return 'N'

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
        return ['N'] * len(no_list)

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
        return ['N'] * len(no_list)

    def _mark_as_read_list(self, user_id, no_list):
        return

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
        return

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
        return

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
        return

    def save_to_database(self, user_id):
        '''
        메모리에 존재하는 특정 사용자의 ReadStatus 를 DB 에 기록하고 메모리에서 지운다.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        '''
        return

    def save_users_read_status_to_database(self, user_ids):
        '''
        주어진 사용자들에 대한 ReadStatus 를 DB 에 기록하고 메모리에서 지운다.

        @type  user_ids: list<int>
        @param user_ids: ReadStatus 를 기록할 사용자들의 고유 id
        '''
        return

    def _save_all_users_to_database(self):
        '''
        메모리에 존재하는 모든 사용자의 ReadStatus 를 DB 에 기록하고 메모리에서 지운다.
        '''
        return

    def get_read_status_loaded_users(self):
        '''
        현재 ReadStatus 정보를 Memory에 들고 있는 사용자의 목록을 구한다.

        @rtype: list<int>
        @return: 사용자 고유 id 의 목록
        '''
        return []

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
