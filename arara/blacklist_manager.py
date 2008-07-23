# -*- coding: utf-8 -*-

import datetime
import time

from arara.util import filter_dict, require_login, is_keys_in_dict
from arara import model
from sqlalchemy.exceptions import InvalidRequestError, IntegrityError

class AlreadyAddedException(Exception):
    pass

class NotExistUSERNAMEException(Exception):
    pass

class NotLoggedIn(Exception):
    pass

BLACKLIST_DICT = ['blacklist_username', 'block_article', 'block_message']
BLACKLIST_LIST_DICT = ['id', 'username', 'blacklisted_user_username', 'blacklisted_date', 'last_modified_date', 'block_article', 'block_message']

class BlacklistManager(object):
    '''
    블랙리스트 처리 관련 클래스
    '''
    def __init__(self):
        # will make list for blacklist member in member_dic, key value is blacklist ex)59
        self.member_dic = {}
        
    #def _prepare_session_username(function):
    #     # Internal member_dic에 사용자 username를 강제 등록한다.
    #    def wrapper(self, session_key, *args):
    #        if not self.member_dic.has_key(self.login_manager.get_session(session_key)[1]['username']):
    #            self.member_dic[self.login_manager.get_session(session_key)[1]['username']] = {}
    #        return function(self, session_key, *args)
    #    return wrapper

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _set_member_manager(self, member_manager):
        self.member_manager = member_manager
    
    def _get_dict(self, item, whitelist):
        item_dict = item.__dict__
        if item_dict['user_id']:
            item_dict['username'] = item.user.username
            del item_dict['user_id']
        if item_dict['blacklisted_user_id']:
            item_dict['blacklisted_user_username'] = item.target_user.username
            del item_dict['blacklisted_user_id']
        filtered_dict = filter_dict(item_dict, whitelist)

        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(filtered_dict)
        return return_list

    @require_login
    def add(self, session_key, blacklist_username, block_article=True, block_message=True):
        '''
        블랙리스트 username 추가

        default 값: article과 message 모두 True

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_username: stirng
        @param blacklist_username: Blacklist Username
        @rtype: boolean, string
        @return:
            1. 추가 성공: True, 'OK'
            2. 추가 실패:
                1. Wrong Dictionary: False, 'WRONG_DICTIONARY'
                2. 존재하지 않는 아이디: False, 'USERNAME_NOT_EXIST'
                3. 이미 추가되어있는 아이디: False, 'ALREADY_ADDED'
                4. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret, user_info = self.login_manager.get_session(session_key)

        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info['username']).one()
        try:
            target_user = session.query(model.User).filter_by(username=blacklist_username).one()
        except InvalidRequestError:
            return False, 'USERNAME_NOT_EXIST'
        integrity_chk = session.query(model.Blacklist).filter_by(user_id=user.id, 
                        blacklisted_user_id=target_user.id).all()
        if integrity_chk:
            return False, 'ALREADY_ADDED'
        new_blacklist = model.Blacklist(user, target_user, block_article, block_message)
        session.save(new_blacklist)
        session.commit()
        return True, 'OK'
       
    @require_login
    def delete(self, session_key, blacklist_username):
        '''
        블랙리스트 username 삭제 

        >>> blacklist.delete(session_key, 'pv457')
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_username: string
        @param blacklist_id: Blacklist USERNAME
        @rtype: boolean, string
        @return:
            1. 삭제 성공: True, 'OK'
            2. 삭제 실패:
                1. 블랙리스트에 존재하지 않는 아이디: False, 'USERNAME_NOT_IN_BLACKLIST'
                2. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        ret, user_info =  self.login_manager.get_session(session_key)

        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info['username']).one()
        try:
            blacklisted_user = session.query(model.User).filter_by(username=blacklist_username).one()
        except InvalidRequestError:
            return False, 'USERNAME_NOT_EXIST'
        try:
            blacklist_to_del = session.query(model.Blacklist).filter_by(user_id=user.id,
                                blacklisted_user_id=blacklisted_user.id).one()
        except InvalidRequestError:
            return False, 'USERNAME_NOT_IN_BLACKLIST'
        session.delete(blacklist_to_del)
        session.commit()
        return True, 'OK'

    @require_login
    def modify(self, session_key, blacklist_dict):
        '''
        블랙리스트 id 수정 

        >>> blacklist.modify(session_key, {'id': 'pv457', 
        'article': 'False', 'message': 'True'})
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_dic: dictionary
        @param blacklist_dic: Blacklist Dictionary
        @rtype: boolean, string
        @return:
            1. 수정 성공: True, 'OK'
            2. 수정 실패:
                1. 블랙리스트에 존재하지 않는 아이디: False, 'USERNAME_NOT_IN_BLACKLIST'
                2. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        #if not is_keys_in_dict(blacklist_dict, BLACKLIST_DICT):
        #    return False, 'WRONG_DICTIONARY'

        ret, user_info = self.login_manager.get_session(session_key)

        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info['username']).one()
        try:
            target_user = session.query(model.User).filter_by(username=blacklist_dict['blacklisted_user_username']).one()
        except InvalidRequestError:
            return False, 'USERNAME_NOT_EXIST'
        try:
            blacklist_to_modify = session.query(model.Blacklist).filter_by(user_id=user.id,
                                    blacklisted_user_id=target_user.id).one()
        except InvalidRequestError:
            return False, 'USERNAME_NOT_IN_BLACKLIST'
        blacklist_to_modify.block_article = blacklist_dict['block_article']
        blacklist_to_modify.block_message = blacklist_dict['block_message']
        blacklist_to_modify.last_modified_date = datetime.datetime.fromtimestamp(time.time())
        session.commit()
        return True, 'OK'

    @require_login
    def list(self,session_key):
        '''
        블랙리스트로 설정한 사람의 목록을 보여줌

        >>> blacklist.list_show(session_key)
        True, [{'id': 'pv457', 'article': 'True', 'message' False'},
        {'id': 'serialx', 'article': 'False', 'message', 'True'}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, list
        @return:
            1. 성공: True, Blacklist Dictionary List
            2. 실패:
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)

        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info['username']).one()
        blacklist_list = session.query(model.Blacklist).filter_by(user_id=user.id).all()
        blacklist_dict_list = self._get_dict_list(blacklist_list, BLACKLIST_LIST_DICT)
        return True, blacklist_dict_list


# vim: set et ts=8 sw=4 sts=4
