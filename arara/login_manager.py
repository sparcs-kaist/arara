# -*- coding: utf-8 -*-

import md5 as hashlib
import logging
import datetime
import time

from arara import model
from util import is_keys_in_dict
from util import log_method_call_with_source

log_method_call = log_method_call_with_source('login_manager')

class LoginManager(object):
    '''
    로그인 처리 관련 클래스
    '''
    
    def __init__(self):
        self.session_dic = {}
        self.logger = logging.getLogger('login_manager')
        self._create_counter_column()

    def _create_counter_column(self):
        session = model.Session()
        visitor = model.Visitor()
        session.save(visitor)
        session.commit()
        session.close()

    def _set_member_manager(self, member_manager):
        self.member_manager = member_manager

    def guest_login(self, guest_ip):
        '''
        guest 로그인 처리를 담당하는 함수
        guest 의 ip를 받은 뒤 guest key를 리턴

        @type  guest_ip: string
        @param guest_ip: Guest IP
        @rtype: string
        @return: True, guest_key
        '''

        return False, 'TEMPORARILY_DISABLED'
        #hash = hashlib.md5('guest'+''+datetime.datetime.today().__str__()).hexdigest()
        #timestamp = datetime.datetime.isoformat(datetime.datetime.now())
        #self.session_dic[hash] = {'username': 'guest', 'ip': guest_ip, 'logintime': timestamp}
        #return True, hash


    def total_visitor(self):
        '''
        방문자 수를 1증가 시켜줌과 동시에 지금까지의 ARAra 방문자 수를 리틴해주는 함수

        @rtype: boolean, integer
        @return:
            1. 성공 시: True, total_visitor_count
            2. 실패 시: False, -1
        '''
        session = model.Session()
        try:
            visitor = session.query(model.Visitor).one()
        except Exception, e: 
            raise
            session.close()
            return False, -1
        visitor.total = visitor.total + 1
        total_visitor_count = visitor.total
        session.commit()
        session.close()
        return True, total_visitor_count

    @log_method_call
    def login(self, username, password, user_ip):
        '''
        로그인 처리를 담당하는 함수.
        아이디와 패스워드를 받은 뒤 User Key를 리턴.

        @type  username: string
        @param username: User Username
        @type  password: string
        @param password: User Password
        @type  user_ip: string
        @param user_ip: User IP
        @rtype: boolean, string
        @return: 
            1. 로그인 성공 시: True, user_key
            2. 로그인 실패 시
                1. 아이디 존재하지 않음: False, 'WRONG_USERNAME'
                2. 패스워드 불일치: False, 'WRONG_PASSWORD'
                3. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'
                4. 이미 로그인된 아이디: False, 'ALREADY_LOGIN'
        '''
        
        ret = []
        success, msg = self.member_manager._authenticate(username, password, user_ip)
        if success:
            #for user_info in self.session_dic.values():
            #    if user_info['username'] == username:
            #        return False, 'ALREADY_LOGIN'
            hash = hashlib.md5(username+password+datetime.datetime.today().__str__()).hexdigest()
            timestamp = datetime.datetime.fromtimestamp(time.time())
            self.session_dic[hash] = {'username': username, 'ip': user_ip, 'nickname': msg['nickname'], 'logintime': msg['last_login_time'], 'current_action': 'login_manager.login()'}
            self.logger.info("User '%s' has LOGGED IN from '%s' as '%s'", username, user_ip, hash)
            return True, hash
        return success, msg

    def logout(self, session_key):
        '''
        로그아웃 처리를 담당하는 함수.

        @type  session_key: string
        @param session_key: User Key
        @rtype: string
        @return:
            1. 로그아웃 성공 시: True, 'OK'
            2. 로그아웃 실패 시
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'
        '''

        try:
            ret, msg = self.member_manager._logout_process(self.session_dic[session_key]['username'])
            if ret:
                self.logger.info("User '%s' has LOGGED OUT", self.session_dic[session_key]['username'])
                self.session_dic.pop(session_key)
                return True, 'OK'
            else:
                return ret, msg
        except KeyError:
            return False, 'NOT_LOGGEDIN'

    def _update_monitor_status(self, session_key, action):
        if self.session_dic.has_key(session_key):
            self.session_dic[session_key]['current_action'] = action
            return True, 'OK'
        else:
            return False, 'NOT_LOGGEDIN'

    def update_session(self, session_key):
        '''
        세션 expire시간을 연장해주는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: integer
        @return:
            1. 업데이트 성공 시: True, 'OK'
            2. 업데이트 실패 시
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'
        '''

        return False, 'NOT_IMPLEMENTED'

    @log_method_call
    def get_session(self, session_key):
        '''
        세션 정보를 반환하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: dictionary
        @return:
            1. 로그인 되어있을 경우: True, self.session_dic {username, user_ip, login_time}
            2. 로그인 되어있지 않을 경우: False, 'NOT_LOGGEDIN'
        '''
        try:
            session_info = self.session_dic[session_key]
            return True, session_info
        except KeyError:
            return False, 'NOT_LOGGEDIN'

    @log_method_call
    def get_current_online(self, session_key):
        '''
        현재 온라인 상태인 사용자를 반환하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 반환 성공: True, List of online users
            2. 반환 실패
                1. 로그인 되지 않은 사용자: False, 'NOT_LOGGEDIN'
        '''

        ret = []
        if self.session_dic.has_key(session_key):
            for user_info in self.session_dic.values():
                ret.append(user_info)
            return True, ret
        else:
            return False, 'NOT_LOGGEDIN'

    @log_method_call
    def is_logged_in(self, session_key):
        '''
        로그인 여부를 체크하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean
        @return:
            1. 로그인 되어있을 경우: True
            2. 로그인 되어있지 않을 경우: False
        '''

        if session_key in self.session_dic:
            return True
        else:
            return False

# vim: set et ts=8 sw=4 sts=4
