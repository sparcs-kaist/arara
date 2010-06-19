#-*- coding: utf-8 -*-
import logging
import unittest
import os
import sys


THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gen-py/'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(ARARA_PATH)

from arara_thrift.ttypes import *
import arara.model
import arara
import arara.server
import arara.model
from etc.arara_settings import SESSION_EXPIRE_TIME
server = None

# Faking time.time (to check time field)
import time
def stub_time():
    return 1.1

def stub_time_2():
    return 1.1 + (SESSION_EXPIRE_TIME / 2)

class LoginManagerTest(unittest.TestCase):
    def setUp(self):
        global server
        # Common preparation for all tests
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        arara.server.server = arara.get_namespace()
        server = arara.get_namespace()
        self.org_time = time.time
        time.time = stub_time

        # Register pipoket
        user_reg_dic = {'username':u'pipoket', 'password':u'pipoket', 'nickname':u'pipoket', 'email':u'pipoket@example.com', 'signature':u'pipoket', 'self_introduction':u'pipoket', 'default_language':u'english' }
        register_key = server.member_manager.register_(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'pipoket', unicode(register_key))

        # Register serialx
        user_reg_dic = {'username':u'serialx', 'password':u'serialx', 'nickname':u'serialx', 'email':u'serialx@example.com', 'signature':u'serialx', 'self_introduction':u'serialx', 'default_language':u'serialx' }
        register_key = server.member_manager.register_(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'serialx', unicode(register_key))

    def testNormalLoginLogout(self):
        # Login as both user
        session_key_pipoket = server.login_manager.login(u'pipoket', u'pipoket', u'143.248.234.145')
        session_key_serialx = server.login_manager.login(u'serialx', u'serialx', u'143.248.234.140')
        # Then logout
        server.login_manager.logout(session_key_pipoket)
        server.login_manager.logout(session_key_serialx)

    def testWrongLogin(self):
        # Wrong Password
        try:
            server.login_manager.login(u'pipoket', u'not_test', '143.248.234.145')
            fail()
        except InvalidOperation:
            pass
        # Not existing user
        try:
            server.login_manager.login(u'not_test', u'test', '143.248.234.145')
            fail()
        except InvalidOperation:
            pass

    def testIsLoggedIn(self):
        session_key = server.login_manager.login(u'pipoket', u'pipoket', '143.248.234.145')
        session_bee = u'thisisnotapropermd5sessionkey...'
        self.assertEqual(False, server.login_manager.is_logged_in(unicode(session_bee)))
        self.assertEqual(True, server.login_manager.is_logged_in(unicode(session_key)))
        server.login_manager.logout(session_key)
        self.assertEqual(False, server.login_manager.is_logged_in(unicode(session_key)))

    def testGetSession(self):
        session_key = server.login_manager.login(u'pipoket', u'pipoket', '143.248.234.145')
        result = server.login_manager.get_session(unicode(session_key))
        self.assertEqual('143.248.234.145', result.ip)
        self.assertEqual(u'pipoket', result.username)
        server.login_manager.logout(session_key)

    def testGetUserId(self):
        session_key = server.login_manager.login(u'pipoket', u'pipoket', '143.248.234.145')
        result = server.login_manager.get_user_id(unicode(session_key))
        self.assertEqual(2, result)
        server.login_manager.logout(session_key)

        session_key = server.login_manager.login(u'SYSOP', u'SYSOP', '143.248.234.145')
        result = server.login_manager.get_user_id(unicode(session_key))
        self.assertEqual(1, result)
        server.login_manager.logout(session_key)

    def testGetUserIp(self):
        session_key1 = server.login_manager.login(u'pipoket', u'pipoket', '143.248.234.145')
        session_key2 = server.login_manager.login(u'SYSOP', u'SYSOP', '143.248.234.146')
        result1 = server.login_manager.get_user_ip(unicode(session_key1))
        result2 = server.login_manager.get_user_ip(unicode(session_key2))
        self.assertEqual("143.248.234.145", result1)
        self.assertEqual("143.248.234.146", result2)
        server.login_manager.logout(session_key1)
        server.login_manager.logout(session_key2)

    def testGetCurrentOnline(self):
        session_key_pipoket = server.login_manager.login(u'pipoket', u'pipoket', '143.248.234.145')
        session_key_serialx = server.login_manager.login(u'serialx', u'serialx', '143.248.234.140')
        session = server.login_manager.get_current_online(session_key_pipoket)
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

        server.login_manager.logout(session_key_serialx)
        server.login_manager.logout(session_key_pipoket)

        try:
            server.login_manager.get_current_online("wrong_key")
            fail()
        except NotLoggedIn:
            pass


    def testWrongLogOut(self):
        try:
            server.login_manager.logout(unicode("wrong_key"))
            fail()
        except NotLoggedIn:
            pass

    def testUpdateMonitorStatus(self):
        # 본 테스트의 목적은 로그인 이후 활동을 하는 사용자가 로그아웃되는것을 막기 위함이다.
        session_key_pipoket = server.login_manager.login(u'pipoket', u'pipoket', u'143.248.234.145')
        time.time = stub_time_2

        server.login_manager._update_monitor_status(session_key_pipoket, "read")
        # XXX 지금은 dictionary 에 직접 접근하는데 ...
        #     last_action_time 을 보는 함수가 없는 탓이다.
        #     어떻게 해야 좋을까? 아흥.
        result = server.login_manager.session_dic[session_key_pipoket]['last_action_time']

        self.assertEqual(result, stub_time_2())

    def tearDown(self):
        time.time = self.org_time
        arara.model.clear_test_database()

    def testCount(self):
        visitors = server.login_manager.total_visitor() 
        self.assertEqual(1, visitors.total_visitor_count)
        self.assertEqual(1, visitors.today_visitor_count)
        visitors = server.login_manager.total_visitor() 
        self.assertEqual(2, visitors.total_visitor_count)
        self.assertEqual(2, visitors.today_visitor_count)
        visitors = server.login_manager.total_visitor() 
        self.assertEqual(3, visitors.total_visitor_count)
        self.assertEqual(3, visitors.today_visitor_count)
        visitors = server.login_manager.total_visitor() 
        self.assertEqual(4, visitors.total_visitor_count)
        self.assertEqual(4, visitors.today_visitor_count)
        # TODO: 하루가 지난 뒤에는 totday_visitor_count 가 0 이 되는 것

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(LoginManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
