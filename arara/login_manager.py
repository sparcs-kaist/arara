# -*- coding: utf-8 -*-

import md5 as hashlib
import logging
import datetime
import thread
import time

from sqlalchemy.exceptions import InvalidRequestError

from arara_thrift.ttypes import *
from arara.model import ReadStatus

from arara import model
from util import is_keys_in_dict
from util import log_method_call_with_source
from util import smart_unicode
from arara.settings import SESSION_EXPIRE_TIME
from arara.server import get_server

log_method_call = log_method_call_with_source('login_manager')

class LoginManager(object):
    '''
    로그인 처리 관련 클래스
    '''
    
    def __init__(self):
        self.session_dic = {}
        self.session_checker = thread.start_new_thread(self._check_session_status, tuple())
        self.logger = logging.getLogger('login_manager')
        self._create_counter_column()

    def _create_counter_column(self):
        session = model.Session()
        try:
            visitor = session.query(model.Visitor).one()
            session.close()
        except InvalidRequestError:
            visitor = model.Visitor()
            session.save(visitor)
            session.commit()
            session.close()

    def _set_member_manager(self, member_manager):
        get_server().member_manager = member_manager

    def guest_login(self, guest_ip):
        '''
        guest 로그인 처리를 담당하는 함수
        guest 의 ip를 받은 뒤 guest key를 리턴

        @type  guest_ip: string
        @param guest_ip: Guest IP
        @rtype: string
        @return: guest_key
        '''

        raise InvalidOperation('temporarily disabled')
        #hash = hashlib.md5('guest'+''+datetime.datetime.today().__str__()).hexdigest()
        #timestamp = datetime.datetime.isoformat(datetime.datetime.now())
        #self.session_dic[hash] = {'username': 'guest', 'ip': guest_ip, 'logintime': timestamp}
        #return True, hash

    @log_method_call
    def total_visitor(self):
        '''
        방문자 수를 1증가 시켜줌과 동시에 
        지금까지의 ARAra 총 방문자 수와 오늘 하루 방문자수를 리틴해주는 함수

        @rtype: arara_thrift.VisitorCount
        @return: 방문자수와 하루 방문자수를 포함한 객체
        '''
        session = model.Session()
        try:
            visitor = session.query(model.Visitor).one()
        except Exception, e: 
            session.close()
            raise InternalError(repr(e))
        visitor.total = visitor.total + 1
        now = datetime.datetime.fromtimestamp(time.time())
        if not now.day == visitor.date.day:
            visitor.today = 0
        visitor.today = visitor.today + 1
        visitor.date = datetime.datetime.fromtimestamp(time.time())
        session.commit()
        session.close()
        visitor_count= {'total_visitor_count':visitor.total, 'today_visitor_count':visitor.today}
        return VisitorCount(**visitor_count)

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
        @rtype: string
        @return: 로그인한 세션 Key
        '''
        username = smart_unicode(username)
        password = smart_unicode(password)
        user_ip = smart_unicode(user_ip)
        ret = []
        msg = get_server().member_manager.authenticate(username, password, user_ip)
        #for user_info in self.session_dic.values():
        #    if user_info['username'] == username:
        #        return False, 'ALREADY_LOGIN'
        hash = hashlib.md5(username+password+datetime.datetime.today().__str__()).hexdigest()
        timestamp = datetime.datetime.fromtimestamp(time.time())
        self.session_dic[hash] = {'username': username, 'ip': user_ip,
                'nickname': msg.nickname, 'logintime': msg.last_login_time,
                'current_action': 'login_manager.login()',
                'last_action_time': datetime.datetime.fromtimestamp(time.time())}
        self.logger.info("User '%s' has LOGGED IN from '%s' as '%s'", username, user_ip, hash)
        return hash

    def logout(self, session_key):
        '''
        로그아웃 처리를 담당하는 함수.

        @type  session_key: string
        @param session_key: User Key
        '''

        try:
            username = self.session_dic[session_key]['username']
            get_server().member_manager._logout_process(username)
            self.logger.info("User '%s' has LOGGED OUT" % username)
            del self.session_dic[session_key]
        except KeyError:
            raise NotLoggedIn()

    def _update_monitor_status(self, session_key, action):
        '''현재 사용자가 어떤 일을 하고있는지 update 하는 메소드.'''
        action = smart_unicode(action)
        if self.session_dic.has_key(session_key):
            self.session_dic[session_key]['current_action'] = action
            return True
        else:
            return False

    def _check_session_status(self):
        while True:
            logger = logging.getLogger('SESSION CLEANER')
            logger.info("=================== SESSION CLEANING STARTED") 
            current_time = datetime.datetime.fromtimestamp(time.time())
            for session_key in self.session_dic.keys():
                session_time = self.session_dic[session_key]['last_action_time']
                username = self.session_dic[session_key]['username']
                diff_time = current_time - session_time
                if diff_time.seconds > SESSION_EXPIRE_TIME:
                    logger.info("==SESSION CLEANER== TARGET DETECTED: USERNAME<%s>" % username)
                    logger.info("==SESSION CLEANER==: SAVING READSTATUS OF %s FROM DATABASE" % username)
                    get_server().read_status_manager.save_to_database(username)
                    del self.session_dic[session_key]
                    logger.warn("==SESSION CLEANER==: USERNAME<%s> SUCCESFULLY DELETED!" % username)
            logger.info("=================== SESSION CLEANING FINISHED") 
            time.sleep(SESSION_EXPIRE_TIME)

    def update_session(self, session_key):
        '''
        세션 expire시간을 연장해주는 함수

        @type  session_key: string
        @param session_key: User Key
        '''
        if self.session_dic.has_key(session_key):
            self.session_dic[session_key]['last_action_time'] = datetime.datetime.fromtimestamp(time.time())
            return True
        else:
            return False
    @log_method_call
    def get_session(self, session_key):
        '''
        세션 정보를 반환하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: arara_thrift.Session
        @return: 세션 정보를 가지는 객체
        '''
        try:
            session_info = self.session_dic[session_key]
            filtered_session_info = {}
            for k, v in session_info.items():
                if k == 'last_action_time':
                    continue
                filtered_session_info[k] = v
                if k == 'last_logout_time':
                    filtered_session_info[k] = datetime2timestamp(v)
            return Session(**filtered_session_info)
        except KeyError:
            raise NotLoggedIn()

    @log_method_call
    def get_current_online(self, session_key):
        '''
        현재 온라인 상태인 사용자를 반환하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: list<Session>
        @return: 접속중인 사용자들의 Session List
        '''

        ret = []
        if self.session_dic.has_key(session_key):
            for user_info in self.session_dic.values():
                del user_info["last_action_time"]
                ret.append(Session(**user_info))
            return ret
        else:
            raise NotLoggedIn()

    @log_method_call
    def is_logged_in(self, session_key):
        '''
        로그인 여부를 체크하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean
        @return: session_key 의 사용자가 로그인 해 있는지 여부
        '''

        if session_key in self.session_dic:
            return True
        else:
            return False

# vim: set et ts=8 sw=4 sts=4
