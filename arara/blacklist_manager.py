# -*- coding: utf-8 -*-

import datetime
import time

from sqlalchemy.exceptions import InvalidRequestError, IntegrityError
from arara import model
from arara.util import filter_dict, require_login, is_keys_in_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import smart_unicode, datetime2timestamp

from arara_thrift.ttypes import *

log_method_call = log_method_call_with_source('blacklist_manager')
log_method_call_important = log_method_call_with_source_important('blacklist_manager')

BLACKLIST_DICT = ['blacklist_username', 'block_article', 'block_message']
BLACKLIST_LIST_DICT = ['id', 'blacklisted_user_nickname', 'blacklisted_user_username', 'blacklisted_date', 'last_modified_date', 'block_article', 'block_message']

class BlacklistManager(object):
    '''
    블랙리스트 처리 관련 클래스
    '''
    def __init__(self, engine):
        '''
        @type  engine: ARAraEngine
        '''
        self.engine = engine

    def _get_dict(self, item, whitelist):
        '''
        @type  item: model.Blacklist
        @type  whitelist: list<string>
        @rtype: ttypes.BlacklistInformation
        '''
        item_dict = item.__dict__
        if item_dict['user_id']:
            item_dict['username'] = item.user.username
            del item_dict['user_id']
        if item_dict['blacklisted_user_id']:
            item_dict['blacklisted_user_username'] = item.target_user.username
            item_dict['blacklisted_user_nickname'] = item.target_user.nickname
            del item_dict['blacklisted_user_id']
        item_dict['last_modified_date'] = \
                datetime2timestamp(item_dict['last_modified_date'])
        item_dict['blacklisted_date'] = \
                datetime2timestamp(item_dict['blacklisted_date'])
        filtered_dict = filter_dict(item_dict, whitelist)

        return BlacklistInformation(**filtered_dict)

    def _get_dict_list(self, raw_list, whitelist):
        '''
        @type  raw_list: iterable<model.Blacklist>
        @type  whitelist: list<string>
        @rtype: list<ttypes.BlacklistInformation>
        '''
        # TODO: generator 화 할 수는 없나?
        return [self._get_dict(item, whitelist) for item in raw_list]

    def _get_user(self, session, username):
        '''
        @type  session: SQLAlchemy Session
        @type  username: string
        @rtype: model.User
        '''
        # TODO: MemberManager 로 옮긴다
        try:
            user = session.query(model.User).filter_by(username=smart_unicode(username)).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('username not exist')
        return user

    @require_login
    @log_method_call_important
    def add_blacklist(self, session_key, username, block_article=True, block_message=True):
        '''
        현재 로그인한 사용자가 차단하고자 하는 새로운 사용자를 Blacklist 에 추가한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  username: string
        @param username: 차단하고자 하는 사용자의 username
        @type  block_article: boolean
        @param block_article: 해당 사용자의 글을 읽지 않을 것인지의 여부
        @type  block_message: boolean
        @param block_message: 해당 사용자의 메시지를 받지 않을 것인지의 여부
        @rtype: void
        @return:
            1. 추가 성공: void
            2. 추가 실패:
                1. Wrong Dictionary: InvalidOperation Exception
                2. 존재하지 않는 아이디: InvalidOperation Exception 
                3. 자기 자신은 등록 불가: InvalidOperation Exception 
                4. 이미 추가되어있는 아이디: InvalidOperation Exception
                5. 로그인되지 않은 사용자: NotLoggedIn Exception
                6. 데이터베이스 오류: InternalError Exception 
        '''
        # TODO: 시삽을 차단하게 허용할 것인가?
        # TODO: block_article, block_message 가 모두 False 라면?
        # TODO: user_id 를 파라메터로 하는 함수 분리
        user_info = self.engine.login_manager.get_session(session_key)
        username = smart_unicode(username)
        if username == user_info.username:
            raise InvalidOperation('cannot add yourself')

        session = model.Session()
        user = self._get_user(session, user_info.username)
        target_user = self._get_user(session, username)

        integrity_chk = session.query(model.Blacklist).filter_by(user_id=user.id, 
                        blacklisted_user_id=target_user.id).all()
        if integrity_chk:
            session.close()
            raise InvalidOperation('already added')
        new_blacklist = model.Blacklist(user, target_user, block_article, block_message)
        session.add(new_blacklist)
        session.commit()
        session.close()
        return
       
    @require_login
    @log_method_call_important
    def delete_blacklist(self, session_key, username):
        '''
        현재 로그인한 사용자가 차단 해제하고자 하는 사용자를 Blacklist 에서 제거한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  username: string
        @param username: 차단을 해제하고자 하는 사용자의 username
        @rtype: void
        @return:
            1. 삭제 성공: void 
            2. 삭제 실패:
                1. 블랙리스트에 존재하지 않는 아이디: InvalidOperation Exception 
                2. 로그인되지 않은 사용자: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: user_id 를 파라메터로 하는 함수 분리
        user_id = self.engine.login_manager.get_user_id(session_key)
        username = smart_unicode(username)

        session = model.Session()
        blacklisted_user = self._get_user(session, username)

        try:
            blacklist_to_del = session.query(model.Blacklist).filter_by(user_id=user_id,
                                blacklisted_user_id=blacklisted_user.id).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('username not in blacklist')
        session.delete(blacklist_to_del)
        session.commit()
        session.close()
        return

    @require_login
    @log_method_call_important
    def modify_blacklist(self, session_key, blacklist_info):
        '''
        현재 로그인한 사용자가 수정하고자 하는 Blacklist 정보를 수정한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  blacklist_info: dict(BLACKLIST_DICT)
        @param blacklist_info: 수정하고자 하는 블랙리스트 정보
        @rtype: void
        @return:
            1. 수정 성공: void
            2. 수정 실패:
                1. 블랙리스트에 존재하지 않는 아이디: InvalidOperation Exception 
                2. 로그인되지 않은 사용자: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: BLACKLIST_DICT 가 어떻게 생겼는지 이 함수 주석에 추가
        # TODO: Blacklist Entry 를 가져오는 함수를 별도로 분리하자
        # TODO: user_id 를 파라메터로 하는 함수 분리
        user_id = self.engine.login_manager.get_user_id(session_key)

        session = model.Session()
        target_user = self._get_user(session, blacklist_info.blacklisted_user_username)
        try:
            blacklist_to_modify = session.query(model.Blacklist).filter_by(user_id=user_id,
                                    blacklisted_user_id=target_user.id).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('username not in blacklist')
        blacklist_to_modify.block_article = blacklist_info.block_article
        blacklist_to_modify.block_message = blacklist_info.block_message
        blacklist_to_modify.last_modified_date = datetime.datetime.fromtimestamp(time.time())
        session.commit()
        session.close()
        return

    @require_login
    @log_method_call
    def get_blacklist(self,session_key):
        '''
        로그인한 사용자의 블랙리스트 목록을 돌려준다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: list<BlacklistInformation>
        @return:
            1. 성공: Blacklist Dictionary List
            2. 실패:
                1. 로그인되지 않은 사용자:InvalidOperation 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: InternalError 'DATABASE_ERROR'
        '''
        # TODO: user_id 를 파라메터로 하는 함수 분리
        user_id = self.engine.login_manager.get_user_id(session_key)
        try:
            session = model.Session()
            blacklist_list = session.query(model.Blacklist).filter_by(user_id=user_id).all()
            session.close()
            blacklist_list = self._get_dict_list(blacklist_list, BLACKLIST_LIST_DICT)
        except:
            session.close()
            raise InternalError('database error')
        return blacklist_list

    @require_login
    @log_method_call
    def get_article_blacklisted_userid_list(self,session_key):
        '''
        사용자가 블랙리스트에 Article 을 차단하겠다고 설정한 사용자들의 고유 id 를 돌려준다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: list<int>
        @return:
            1. 성공: 차단된 사용자들의 고유 id 목록
            2. 실패:
                1. 로그인되지 않은 사용자: InvalidOperation('NOT_LOGGEDIN')
                2. 데이터베이스 오류: InternalError('DATABASE_ERROR')
        '''
        # TODO: user_id 를 파라메터로 하는 함수 분리

        user_id = self.engine.login_manager.get_user_id(session_key)
        try:
            session = model.Session()
            raw_blacklist = session.query(model.Blacklist).filter_by(user_id=user_id, block_article=True).all()
            session.close()
            userid_blacklist = [x.blacklisted_user_id for x in raw_blacklist]
        except:
            session.close()
            raise InternalError('database error')
        return userid_blacklist

# vim: set et ts=8 sw=4 sts=4
