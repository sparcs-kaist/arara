# -*- coding: utf-8 -*-

import md5 as hashlib
import logging
import datetime
import thread
import time

from sqlalchemy.exceptions import InvalidRequestError, ConcurrentModificationError

from arara_thrift.ttypes import *

from arara import model
from util import log_method_call_with_source
from util import smart_unicode

from etc.arara_settings import SESSION_EXPIRE_TIME

log_method_call = log_method_call_with_source('login_manager')

class LoginManager(object):
    '''
    로그인 처리 관련 클래스
    '''
    
    def __init__(self, engine):
        '''
        @type  engine: ARAraEngine
        '''
        self.lock_session_dic = thread.allocate_lock()
        self.engine = engine
        self.session_dic = {}
        self.logger = logging.getLogger('login_manager')
        self._create_counter_column()
        # Engine 이 가동중인 동안 True, 가동을 멈추면 False 가 되는 변수
        self.engine_online = True
        # Thread 가동 시작
        self.session_checker = thread.start_new_thread(self._check_session_status, tuple())

    def shutdown(self):
        '''
        LoginManager 의 작동을 멈춘다. 즉 Session Cleaner thread 의 작동을 멈춘다.
        '''
        self.engine_online = False

    def _create_counter_column(self):
        '''
        일일방문자 / 전체방문자를 저장할 객체를 DB 에 만든다.
        '''
        # TODO: Exception 을 발생시키는 것보단 count 등을 쓰는 게 낫지 않을까?
        session = model.Session()
        try:
            visitor = session.query(model.Visitor).one()
            session.close()
        except InvalidRequestError:
            visitor = model.Visitor()
            session.add(visitor)
            session.commit()
            session.close()

    def guest_login(self, guest_ip):
        '''
        guest 로그인 처리를 담당하는 함수
        guest 의 ip를 받은 뒤 guest key를 리턴

        @type  guest_ip: string
        @param guest_ip: Guest IP
        @rtype: string
        @return: guest_key
        '''
        # TODO: guest login 이 필요하지 않다면 그냥 지우도록 하자.

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
        @return: 총 방문자수와 하루 방문자수를 포함한 객체
        '''
        # TODO: 사실 가장 예쁘게 하는 방법은 visitor 숫자를 늘리는 메소드를
        #       별도의 thread 로 빼 버리고 이 함수 자신은 순수하게 DB를
        #       읽어오기만 하는 것이 아닐지 ...
        RETRY_COUNT = 20

        session = model.Session()
        total = None
        today = None
        now = datetime.datetime.fromtimestamp(time.time())
        # ConcurrentModificationError 가 나면 RETRY_COUNT 회 재시도하도록 해 보자.
        for i in xrange(RETRY_COUNT):
            try:
                visitor = session.query(model.Visitor).first()
                visitor.total = visitor.total + 1
                if not now.day == visitor.date.day:
                    visitor.today = 0
                visitor.today = visitor.today + 1
                visitor.date = now
                total = visitor.total
                today = visitor.today
                session.commit()
                break
            except ConcurrentModificationError:
                # 끝까지 실패하면 로깅메시지 하나 띄워주자.
                session.rollback()
                if i == RETRY_COUNT - 1:
                    visitor = session.query(model.Visitor).first()
                    total = visitor.total
                    today = visitor.today
                    self.logger.warning("Internal Error occur on LoginManager.total_visitor(): Due t the repeated ConcurrentModificationError, can't update Counter information.")
                continue

        session.close()
        visitor_count= {'total_visitor_count':total, 'today_visitor_count':today}
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
        @return: 사용자 Login Session
        '''
        # TODO: login 함수가 고민할 필요가 없는 Exception 들은 그냥 넘기기 (더 이상 매니저간 통신은 Thrift 를 거치지 않는다)
        username = smart_unicode(username)
        password = smart_unicode(password)
        user_ip = smart_unicode(user_ip)
        # 가끔 Thrift 가 맛이 가서 LoginManager -> MemberManager 통신이 끊어질 때가 있다.
        # 이런 경우 Thrift 자체 Timeout 이 지난 뒤에 Error 가 돌아가므로, InternalError 로 에쁘게 Wrapping 한다.
        try:
            msg = self.engine.member_manager.authenticate(username, password, user_ip)
        except InvalidOperation:
            raise
        except InternalError:
            raise
        except Exception, e:
            self.logger.warning("Internal Error occur on MemberManager.authenticate(): %s" % repr(e))
            raise InternalError("Ask SYSOP")

        with self.lock_session_dic:
            hash = hashlib.md5(username+password+datetime.datetime.today().__str__()).hexdigest()
            self.session_dic[hash] = {'id': msg.id, 'username': username, 'ip': user_ip,
                    'nickname': msg.nickname, 'logintime': msg.last_login_time,
                    'current_action': 'login_manager.login()',
                    'last_action_time': time.time()}
            self.logger.info("User '%s' has LOGGED IN from '%s' as '%s'", username, user_ip, hash)
        return hash

    def logout(self, session_key):
        '''
        로그아웃 처리를 담당하는 함수.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        '''

        try:
            with self.lock_session_dic:
                username = self.session_dic[session_key]['username']
                self.engine.member_manager._logout_process(username)
                self.logger.info("User '%s' has LOGGED OUT" % username)
                del self.session_dic[session_key]
        except KeyError:
            raise NotLoggedIn()

    def _update_monitor_status(self, session_key, action):
        '''
        현재 사용자가 어떤 일을 하고있는지 update 하는 메소드.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  action: string
        @param action: 사용자가 취하고 있는 동작
        @rtype: boolean
        @return: 사용자가 로그인 중이면 True, 아니면 False
        '''
        # TODO: 이 함수를 누가 호출하는지 보고, 왜 T/F 가 필요한지 확인하기
        action = smart_unicode(action)  
        with self.lock_session_dic:
            if self.session_dic.has_key(session_key):
                self.session_dic[session_key]['current_action'] = action
                self.update_session(session_key)
                return True
            else:
                return False
    
    def _clean_specific_session(self, session_key):
        '''
        주어진 사용자가 장시간 작업이 없었다면 Logout 시킨다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        '''
        if not self.session_dic.has_key(session_key):
            # 이미 로그아웃한 사용자라면 이하의 절차가 필요없다.
            return

        with self.lock_session_dic:
            current_time = time.time()
            session_time = self.session_dic[session_key]['last_action_time']
            diff_time = current_time - session_time
            if diff_time > SESSION_EXPIRE_TIME:
                try:
                    self.logout(session_key)
                except NotLoggedIn:
                    # 이미 로그아웃했다면 특별한 문제가 아니다.
                    pass

    def _check_session_status(self):
        '''
        정기적으로 실행되면서 장시간 작업이 없었던 사용자를 Logout 시킨다.
        '''
        while self.engine_online:
            logger = logging.getLogger('SESSION CLEANER')
            logger.info("=================== SESSION CLEANING STARTED") 

            try:
                for session_key in self.session_dic.keys():
                    self._clean_specific_session(session_key)
            except Exception:
                import traceback
                logger.exception("EXCEPTION at SESSION CLEANER : \n%s", traceback.format_exc())

            logger.info("=================== SESSION CLEANING FINISHED") 
            time.sleep(SESSION_EXPIRE_TIME)

    def update_session(self, session_key):
        '''
        세션 expire시간을 연장해주는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: boolean
        @return:
            사용자가 로그인중이면 True, 아니면 False
        '''
        # TODO: 이 함수는 왜 T/F 를 리턴하는가?
        if self.session_dic.has_key(session_key):
            self.session_dic[session_key]['last_action_time'] = time.time()
            return True
        else:
            return False

    @log_method_call
    def get_session(self, session_key):
        '''
        세션 정보를 반환하는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: ttypes.Session
        @return: 세션 정보를 가지는 객체
        '''
        # TODO: filter_dict 함수 등을 쓰도록 변경
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
    def get_user_id(self, session_key):
        '''
        세션의 사용자 id 만을 반환하는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: i32
        @return: 해당 세션의 사용자의 internal id
        '''
        # TODO: check_logged_in 같은 것으로 감싸면 구현이 좀 더 깔끔하지 않을까
        try:
            return self.session_dic[session_key]['id']
        except KeyError:
            raise NotLoggedIn()

    @log_method_call
    def get_user_ip(self, session_key):
        '''
        세션의 사용자 ip 만을 반환하는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: string
        @return: 세션의 사용자 ip
        '''
        # TODO: check_logged_in 같은 것으로 감싸면 구현이 좀 더 깔끔하지 않을까
        try:
            return self.session_dic[session_key]['ip']
        except KeyError:
            raise NotLoggedIn()

    @log_method_call
    def get_current_online(self, session_key):
        '''
        현재 온라인 상태인 사용자를 반환하는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: list<Session>
        @return: 접속중인 사용자들의 Session List
        '''
        # TODO: check_logged_in 같은 것으로 감싸면 구현이 좀 더 깔끔하지 않을까

        ret = []
        with self.lock_session_dic:
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
        @param session_key: 사용자 Login Session
        @rtype: boolean
        @return: session_key 의 사용자가 로그인 해 있는지 여부
        '''
        # TODO: is_logged_in 의 결과에 따라 Exception 을 Raise 하는 check_logged_in 을 만들까?

        if session_key in self.session_dic:
            return True
        else:
            return False

# vim: set et ts=8 sw=4 sts=4
