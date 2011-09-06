#-*- coding: utf-8 -*-
import datetime
import unittest
import os
import sys
import time

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gen-py/'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(ARARA_PATH)

from arara.test.test_common import AraraTestBase
from arara_thrift.ttypes import *
from etc.arara_settings import SESSION_EXPIRE_TIME
from arara import model

# Faking time.time (to check time field)
def stub_time():
    return 1.1

def stub_time_2():
    return 1.1 + (SESSION_EXPIRE_TIME / 2)

def stub_time_3():
    return 1.1 + 86400 # one day

class LoginManagerTest(AraraTestBase):
    def setUp(self):
        # Common preparation for all tests
        super(LoginManagerTest, self).setUp()
        
        self.org_time = time.time
        time.time = stub_time

    def _register_user(self, username, manual_setting = {}):
        user_reg_dic = {'username': username, 'password': username, 'nickname': username, 'email': username + '@kaist.ac.kr', 'signature': username, 'self_introduction': username, 'default_language': u'english', 'campus': u'Daejeon'}
        for key in manual_setting:
            if key in user_reg_dic:
                user_reg_dic[key] = manual_setting[key]
        registration_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(username, registration_key)

    def test_login(self):
        self._register_user(u'pipoket')

        # Successfully log in
        self.engine.login_manager.login(u'pipoket', u'pipoket', u'143.248.234.145')

        # Wrong Password
        try:
            self.engine.login_manager.login(u'pipoket', u'not_test', '143.248.234.145')
            self.fail("with wrong password, user can't log in")
        except InvalidOperation:
            pass
        # Not existing user
        try:
            self.engine.login_manager.login(u'hodduc', u'hodduc', '143.248.234.145')
            self.fail("nonexisting user can't login")
        except InvalidOperation:
            pass

        # TODO: LoginManager 의 login 메소드가 잘 작동했는지를 검사하려면,
        #       사실 session_key 가 바르게 생성되었는지 검토하는 것이 필요.

        # TODO: Last Login Time 정보가 바르게 기록되었는지를 검사한다

    def test_logout(self):
        self._register_user(u'hodduc')
        session_key = self.engine.login_manager.login(u'hodduc', u'hodduc', '143.248.234.145')

        # Logout 성공
        self.engine.login_manager.logout(session_key)

        # Login 되지 않은 Session Key 로는 logout 할 수 없어야 한다
        try:
            self.engine.login_manager.logout(session_key)
            self.fail("One can't logout with not logged in session key")
        except NotLoggedIn:
            pass

        # TODO: Last Logout Time 정보가 바르게 기록되는지를 검사한다

    def test_is_logged_in(self):
        self._register_user(u'panda')

        # 로그인을 통해 발행되지 않은 session key 는 False
        session_key = u'thisisnotapropermd5sessionkey...'
        self.assertEqual(False, self.engine.login_manager.is_logged_in(unicode(session_key)))

        # 로그인을 통해 발행된 session key 는 True
        session_key = self.engine.login_manager.login(u'panda', u'panda', '143.248.234.145')
        self.assertEqual(True, self.engine.login_manager.is_logged_in(unicode(session_key)))
        
        # 로그아웃하면 False
        self.engine.login_manager.logout(session_key)
        self.assertEqual(False, self.engine.login_manager.is_logged_in(unicode(session_key)))

    def test_get_session(self):
        self._register_user(u'pipoket')
        session_key = self.engine.login_manager.login(u'pipoket', u'pipoket', '143.248.234.145')
        result = self.engine.login_manager.get_session(unicode(session_key))
        self.assertEqual('143.248.234.145', result.ip)
        self.assertEqual(u'pipoket', result.username)

    def test_get_user_id(self):
        # SYSOP 은 1
        session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', '143.248.234.145')
        result = self.engine.login_manager.get_user_id(unicode(session_key))
        self.assertEqual(1, result)
        # pipoket 은 2
        self._register_user(u'pipoket')
        session_key = self.engine.login_manager.login(u'pipoket', u'pipoket', '143.248.234.145')
        result = self.engine.login_manager.get_user_id(unicode(session_key))
        self.assertEqual(2, result)
        # 로그아웃한 경우에는 안된다
        self.engine.login_manager.logout(session_key)
        try:
            self.engine.login_manager.get_user_id(unicode(session_key))
            self.fail("User already logged out, but was able to get user_id")
        except NotLoggedIn:
            pass

    def test_get_user_id_wo_error(self):
        self._register_user(u'panda')
        # 정상적인 경우
        session_key = self.engine.login_manager.login(u'panda', u'panda', '143.248.234.145')
        result = self.engine.login_manager.get_user_id_wo_error(unicode(session_key))
        self.assertEqual(2, result)

        # 이미 로그아웃한 경우
        self.engine.login_manager.logout(session_key)
        result = self.engine.login_manager.get_user_id_wo_error(unicode(session_key))
        self.assertEqual(-1, result)

    def test_get_user_ip(self):
        self._register_user(u"sillo")

        # 서로 다른 두 IP 에 대하여 검사한다
        session_key1 = self.engine.login_manager.login(u'sillo', u'sillo', '143.248.234.145')
        session_key2 = self.engine.login_manager.login(u'SYSOP', u'SYSOP', '143.248.234.146')
        result1 = self.engine.login_manager.get_user_ip(unicode(session_key1))
        result2 = self.engine.login_manager.get_user_ip(unicode(session_key2))
        self.assertEqual("143.248.234.145", result1)
        self.assertEqual("143.248.234.146", result2)

    def test_get_current_online(self):
        self._register_user(u'pipoket')
        self._register_user(u'serialx')
        session_key_pipoket = self.engine.login_manager.login(u'pipoket', u'pipoket', '143.248.234.145')
        session_key_serialx = self.engine.login_manager.login(u'serialx', u'serialx', '143.248.234.140')
        session = self.engine.login_manager.get_current_online(session_key_pipoket)
        pipoket_dict = session[0].__dict__
        pipoket_dict_must_be = {'username': u'pipoket', 'ip': u'143.248.234.145', 'current_action': 'login_manager.login()', 'nickname': u'pipoket', 'logintime': 1.1000000000000001, 'id': 2}

        serialx_dict = session[1].__dict__
        serialx_dict_must_be = {'username': u'serialx', 'ip': u'143.248.234.140', 'current_action': 'login_manager.login()', 'nickname': u'serialx', 'logintime': 1.1000000000000001, 'id': 3}
        self.assertEqual(len(pipoket_dict.keys()), len(pipoket_dict_must_be.keys()))
        for keys in pipoket_dict.keys():
            self.assertEqual(pipoket_dict[keys], pipoket_dict_must_be[keys])
        self.assertEqual(len(serialx_dict.keys()), len(serialx_dict_must_be.keys()))
        for keys in serialx_dict.keys():
            self.assertEqual(serialx_dict[keys], serialx_dict_must_be[keys])

        self.engine.login_manager.logout(session_key_serialx)
        self.engine.login_manager.logout(session_key_pipoket)

        try:
            self.engine.login_manager.get_current_online("session_key_serialx")
            self.fail("get_current_online can't be called by someone who is not logged in")
        except NotLoggedIn:
            pass

    def testUpdateMonitorStatus(self):
        # 본 테스트의 목적은 로그인 이후 활동을 하는 사용자가 로그아웃되는것을 막기 위함이다.
        self._register_user(u'pipoket')
        session_key_pipoket = self.engine.login_manager.login(u'pipoket', u'pipoket', u'143.248.234.145')
        time.time = stub_time_2

        self.engine.login_manager._update_monitor_status(session_key_pipoket, "read")
        # XXX 지금은 dictionary 에 직접 접근하는데 ...
        #     last_action_time 을 보는 함수가 없는 탓이다.
        #     어떻게 해야 좋을까? 아흥.
        result = self.engine.login_manager.session_dic[session_key_pipoket]['last_action_time']

        self.assertEqual(result, stub_time_2())

    def tearDown(self):
        time.time = self.org_time

        # Common tearDown
        super(LoginManagerTest, self).tearDown()

    def test_count(self):
        visitors = self.engine.login_manager.total_visitor() 
        self.assertEqual(1, visitors.total_visitor_count)
        self.assertEqual(1, visitors.today_visitor_count)
        visitors = self.engine.login_manager.total_visitor() 
        self.assertEqual(2, visitors.total_visitor_count)
        self.assertEqual(2, visitors.today_visitor_count)
        # 하루가 지난다. today_visitor_count 는 다시 1부터 올라간다
        time.time = stub_time_3
        visitors = self.engine.login_manager.total_visitor() 
        self.assertEqual(3, visitors.total_visitor_count)
        self.assertEqual(1, visitors.today_visitor_count)
        visitors = self.engine.login_manager.total_visitor() 
        self.assertEqual(4, visitors.total_visitor_count)
        self.assertEqual(2, visitors.today_visitor_count)

    def test_get_expired_sesion_list(self):
        # 로그인한 사용자가 없을 때
        result = self.engine.login_manager.get_expired_sessions()
        self.assertEqual([], result)

        # 한 명의 사용자가 로그인했지만 아직 Expire 되지 않았을 때
        self._register_user(u'panda')
        panda_session_key = self.engine.login_manager.login(u'panda', u'panda', '127.0.0.1')
        result = self.engine.login_manager.get_expired_sessions()
        self.assertEqual([], result)

        # 그 사용자가 Expire 되었을 때
        def stub_time_new():
            return 1.1 + SESSION_EXPIRE_TIME + 1
        time.time = stub_time_new

        result = self.engine.login_manager.get_expired_sessions()
        self.assertEqual([(panda_session_key, 2)], result)

    def test_get_active_sesions(self):
        # 로그인한 사용자가 없을 때
        result = self.engine.login_manager.get_active_sessions()
        self.assertEqual([], result)

        # 한 명의 사용자가 로그인했지만 아직 Expire 되지 않았을 때
        self._register_user(u'panda')
        panda_session_key = self.engine.login_manager.login(u'panda', u'panda', '127.0.0.1')
        result = self.engine.login_manager.get_active_sessions()
        self.assertEqual([(panda_session_key, 2)], result)

        # 그 사용자가 Expire 되었을 때
        def stub_time_new():
            return 1.1 + SESSION_EXPIRE_TIME + 1
        time.time = stub_time_new

        result = self.engine.login_manager.get_active_sessions()
        self.assertEqual([], result)

    def test_cleanup_expired_sessions(self):
        # 테스트 상황 설계
        # 1) 2명의 사용자 모두 ReadStatus 가 로드되어 있음
        # 2) 이중 1명만 Session 이 Expire 되어야 함
        session_key_panda = self.register_and_login(u'panda')  # user 2
        session_key_sillo = self.register_and_login(u'sillo')  # user 3
        self.engine.read_status_manager._initialize_data(2)
        self.engine.read_status_manager._initialize_data(3)
        def stub_time_new():
            return 1.1 + SESSION_EXPIRE_TIME + 1
        time.time = stub_time_new
        self.engine.login_manager.update_session(session_key_sillo)

        self.engine.login_manager.cleanup_expired_sessions()

        # LoginManager
        self.assertEqual(
                {session_key_sillo: {'username': u'sillo',
                        'current_action': 'login_manager.login()',
                        'ip': u'127.0.0.1',
                        'logintime': 1.1000000000000001,
                        'last_action_time': 3612.0999999999999,
                        'nickname': u'sillo',
                        'id': 3}},
                self.engine.login_manager.session_dic)
        # MemberManager
        expect = datetime.datetime.fromtimestamp(1.1 + SESSION_EXPIRE_TIME + 1)
        result = model.Session().query(model.User).filter_by(id=2).one()
        self.assertEqual(expect, result.last_logout_time)
        # ReadStatusManager
        self.assertEqual([3],
                self.engine.read_status_manager.read_status.keys())
        self.assertEqual([(0, 'N')],
                self.engine.read_status_manager.read_status[3].data)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(LoginManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
