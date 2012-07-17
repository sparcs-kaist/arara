# -*- coding: utf-8 -*-

import collections
import hashlib
import logging
import datetime
import time
import UserDict

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import ConcurrentModificationError, NoResultFound, StaleDataError

from libs import smart_unicode

from arara_thrift.ttypes import *

from arara import arara_manager
from arara import model
from util import log_method_call_with_source, log_method_call_with_source_duration

from etc import arara_settings
from etc.arara_settings import SESSION_EXPIRE_TIME

log_method_call = log_method_call_with_source('login_manager')
log_method_call_duration = log_method_call_with_source_duration('login_manager')


class DictSessionStore(UserDict.UserDict):
    '''
    현재 Login되어 있는 사용자들의 Session을 dictionary로 저장한다.
    사용시 LoginManager는 Backend 서버에 단일 객체만 존재해야 한다.
    '''
    pass


class DatabaseSessionStore(collections.MutableMapping):
    '''
    현재 Login되어 있는 사용자들의 Session을 DB에 저장한다.
    '''

    def __contains__(self, key):
        session = model.Session()
        try:
            login_session = session.query(model.LoginSession).filter_by(session_key=key).one()
            session.close()
            return True
        except NoResultFound:
            session.close()
            return False

    def __getitem__(self, key):
        session = model.Session()
        try:
            login_session = session.query(model.LoginSession).filter_by(session_key=key).one()
            session.close()
            return login_session.session_data
        except NoResultFound:
            session.close()
            raise KeyError()

    def __setitem__(self, key, value):
        session = model.Session()
        try:
            # 로그인되어 있는 사용자의 경우 DB의 해당 row에 새로운 값을 기록한다
            login_session = session.query(model.LoginSession).filter_by(session_key=key).one()
            login_session.session_data = value
        except NoResultFound:
            # 로그인되어 있지 않은 사용자의 경우 DB에 새로운 row를 생성한다
            login_session = model.LoginSession(key, value, datetime.datetime.now())
            session.add(login_session)
        session.commit()
        session.close()

    def __delitem__(self, key):
        session = model.Session()
        try:
            login_session = session.query(model.LoginSession).filter_by(session_key=key).one()
            session.delete(login_session)
            session.commit()
            session.close()
        except NoResultFound:
            # 이미 로그아웃된 세션에 대하여 로그아웃을 시도한 경우
            # session.one() 에서 발생함.
            # 어차피 로그아웃되어 있는 것이므로 무시해도 좋다
            session.close()
        except StaleDataError:
            # 같은 사용자 Login Session에 대하여 로그아웃을 시도한 경우
            # session.delete() 에서 발생함.
            # 어차피 삭제된 것이므로 무시해도 괜찮다.
            session.close()

    def __iter__(self):
        session = model.Session()
        result = (x.session_key for x in session.query(model.LoginSession).all())
        session.close()
        return result

    def __len__(self):
        session = model.Session()
        result = session.query(model.LoginSession).count()
        session.close()
        return result


class LoginManager(arara_manager.ARAraManager):
    '''
    로그인 처리 관련 클래스
    '''
    
    def __init__(self, engine):
        '''
        @type  engine: ARAraEngine
        '''
        super(LoginManager, self).__init__(engine)
        if arara_settings.SESSION_TYPE == "dict":
            self.session_dic = DictSessionStore()
        elif arara_settings.SESSION_TYPE == "db":
            self.session_dic = DatabaseSessionStore()
        else:  # Wrong Setting
            raise InternalError("Wrong value for arara_settings.SESSION_TYPE")
        self.logger = logging.getLogger('login_manager')
        self._create_counter_column()
        # Engine 이 가동중인 동안 True, 가동을 멈추면 False 가 되는 변수
        self.engine_online = True
        # Terminate Session 을 위하여
        self.terminated_done = None

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
        아이디와 패스워드를 받은 뒤 사용자 Login Session를 리턴.

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

        # 2010.09.29. 성능 문제로 Lock 을 제거한다.
        # with self.lock_session_dic:
        hash = hashlib.md5(username+password+datetime.datetime.today().__str__()).hexdigest()
        self.session_dic[hash] = {'id': msg.id, 'username': username, 'ip': user_ip,
                'nickname': msg.nickname, 'logintime': msg.last_login_time,
                'current_action': 'login_manager.login()',
                'last_action_time': time.time()}
        self.logger.info("User '%s' has LOGGED IN from '%s' as '%s'", username, user_ip, hash)
        return hash

    def _logout(self, session_key):
        '''
        Thread-Safety 가 없는, 로그아웃 처리 담당 함수.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        '''
        try:
            user_id  = self.session_dic[session_key]['id']
            username = self.session_dic[session_key]['username']
            self.engine.member_manager.logout_process(user_id)
            self.engine.read_status_manager.save_to_database(user_id)
            del self.session_dic[session_key]
            self.logger.info("User '%s' has LOGGED OUT" % username)
        except KeyError:
            raise NotLoggedIn()

    def logout(self, session_key):
        '''
        로그아웃 처리를 담당하는 함수.
        사실상 Thread-safety Wrapper for _logout 이다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        '''
        # 2010.09.29. 성능 문제로 Lock 을 제거.
        # with self.lock_session_dic:
        self._logout(session_key)

    def _update_monitor_status(self, session_key, action):
        '''
        현재 사용자가 어떤 일을 하고있는지 update 하는 메소드.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  action: string
        @param action: 사용자가 취하고 있는 동작
        @rtype: bool
        @return: 사용자가 로그인 중이면 True, 아니면 False
        '''
        # TODO: 이 함수를 누가 호출하는지 보고, 왜 T/F 가 필요한지 확인하기
        action = smart_unicode(action)  
        try:
            if session_key in self.session_dic:
                # self.session_dic 구현에 상관없이 갱신된 값이 저장되도록 설정
                user_session = self.session_dic[session_key]
                user_session['current_action'] = action
                self.session_dic[session_key] = user_session
                # last_action_time 갱신
                self.update_session(session_key)
                return True
            else:
                return False
        except KeyError:
            return False
    
    def update_session(self, session_key):
        '''
        세션 expire시간을 연장해주는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: bool
        @return:
            사용자가 로그인중이면 True, 아니면 False
        '''
        # TODO: 이 함수는 왜 T/F 를 리턴하는가?
        if session_key in self.session_dic:
            # self.session_dic 구현에 상관없이 갱신된 값이 저장되도록 설정
            user_session = self.session_dic[session_key]
            user_session['last_action_time'] = time.time()
            self.session_dic[session_key] = user_session
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
    def get_user_id_wo_error(self, session_key):
        '''
        세션의 사용자 id 만을 반환하는 함수.
        만일 로그인되지 않는 사용자이거나 하면 -1 을 리턴한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: i32
        @return: 해당 세션의 사용자의 internal id 혹은 -1
        '''
        if session_key in self.session_dic:
            try:
                return self.session_dic[session_key]['id']
            except KeyError:
                return -1
        else:
            return -1

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
        지금은 구현이 제대로 되어 있지 않다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: list<Session>
        @return: 접속중인 사용자들의 Session List
        '''
        # TODO: check_logged_in 같은 것으로 감싸면 구현이 좀 더 깔끔하지 않을까

        ret = []
        if session_key in self.session_dic:
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
        @rtype: bool
        @return: session_key 의 사용자가 로그인 해 있는지 여부
        '''
        # TODO: is_logged_in 의 결과에 따라 Exception 을 Raise 하는 check_logged_in 을 만들까?

        if session_key in self.session_dic:
            return True
        else:
            return False

    @log_method_call_duration
    def terminate_all_sessions(self):
        '''
        강제로 모든 Session 을 꺼버린다.
        '''
        self.logger.info("=================== SESSION TERMINATION STARTED") 
        self.engine_online = False
        ids = [x['id'] for x in self.session_dic.values()]
        self.engine.member_manager._update_last_logout_time(ids)
        self.engine.read_status_manager._save_all_users_to_database()
        self.logger.info("=================== SESSION TERMINATION FINISHED") 

    @log_method_call_duration
    def get_expired_sessions(self):
        '''
        장시간 작업이 없었던 사용자들의 Session 목록을 만든다.

        @rtype: list<(str, int)>
        @return: 사용자 Login Session과 각 Session Key 별 사용자 고유 id의 목록
        '''
        current_time = time.time()
        expired_time = current_time - SESSION_EXPIRE_TIME

        expired_sessions = [(session_key, session['id'])
                for session_key, session in self.session_dic.iteritems()
                if session['last_action_time'] < expired_time]

        return expired_sessions

    @log_method_call_duration
    def get_active_sessions(self):
        '''
        최근 작업이 있었던 사용자들의 Session 목록을 만든다.
        get_expired_sessions 의 반대 개념.

        @rtype: list<(str, int)>
        @return: 사용자 Login Session과 각 Session Key 별 사용자 고유 id의 목록
        '''
        current_time = time.time()
        expired_time = current_time - SESSION_EXPIRE_TIME

        active_sessions = [(session_key, session['id'])
                for session_key, session in self.session_dic.iteritems()
                if session['last_action_time'] >= expired_time]

        return active_sessions

    @log_method_call_duration
    def cleanup_expired_sessions(self):
        '''
        사용자들 중 Session Expire time 이 지난 사용자들을 로그아웃시킨다.
        '''
        expired_sessions = self.get_expired_sessions()

        user_ids = [x[1] for x in expired_sessions]
        self.engine.member_manager.update_last_logout_time(user_ids)
        self.engine.read_status_manager.save_users_read_status_to_database(user_ids)

        for session_key, user_id in expired_sessions:
            try:
                del self.session_dic[session_key]
            except KeyError:  # 이 함수 시행중 로그아웃된 경우
                pass

    def debug__check_session(self, session_key, username, user_ip):
        '''
        session_key에 따른 정보와 frontend 측의 username이 불일치할경우에 불리는 함수로, 관련 정보를 logging 하는 debug용 함수이다
        #457번 티켓(다른 사용자로 로그인되는 문제)의 해결을 위한 임시 함수로, 문제가 해결되면 제거하도록 하자.
        '''
        self.logger.error(' XXX   Session mismatch detected   on %s XXX ' % user_ip)
        self.logger.error(' 1. given session key returned by login_manager.login:' + session_key)
        self.logger.error(' 2. session info (backend, may be wrong): ' + str(self.session_dic.get(session_key, 'NO INFO IN DICT')))
        self.logger.error(' 3. actual username (frontend, always true): ' + username)
        self.logger.error(' 4. related sessions .... ')

        related_user = (username, self.get_user_id(session_key))
        related_sess = [(session_key, session)
                for session_key, session in self.session_dic.iteritems()
                if session['username'] in related_user]

        for k, v in related_sess:
            self.logger.error(' (%s): %s' % (k, str(v)))

        self.logger.error(' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ')


    __public__ = [
            guest_login,
            total_visitor,
            login,
            logout,
            update_session,
            get_session,
            get_user_id,
            get_user_ip,
            get_current_online,
            is_logged_in,
            terminate_all_sessions,
            get_expired_sessions,
            get_active_sessions,
            cleanup_expired_sessions,
            debug__check_session]
