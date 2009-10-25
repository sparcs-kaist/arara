#-*- coding: utf-8 -*-
import unittest
import os
import sys
import logging


THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gen-py/'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(ARARA_PATH)

from arara_thrift.ttypes import *
import arara.model
import arara
import arara.server
import arara.model
server = None

class MemberManagerTest(unittest.TestCase):
    def setUp(self):
        global server
        # Common preparation for all tests
        arara.model.init_test_database()
        arara.server.server = arara.get_namespace()
        server = arara.get_namespace()

        # Regiister one user, combacsa
        user_reg_dic = {'username':u'combacsa', 'password':u'combacsa', 'nickname':u'combacsa', 'email':u'combacsa@example.com', 'signature':u'combacsa', 'self_introduction':u'combacsa', 'default_language':u'english' }
        register_key = server.member_manager.register(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'combacsa', unicode(register_key))

        # Register one user, serialx
        user_reg_dic = {'username':u'serialx', 'password':u'serialx', 'nickname':u'serialx', 'email':u'serialx@example.com', 'signature':u'serialx', 'self_introduction':u'serialx', 'default_language':u'english' }
        register_key = server.member_manager.register(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'serialx', unicode(register_key))

    def testAddMikkang(self):
        user_reg_dic = {'username':u'mikkang', 'password':u'mikkang', 'nickname':u'mikkang', 'email':u'mikkang@example.com', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english' }
        # Check this user is not yet registered
        self.assertEqual(False, server.member_manager.is_registered(user_reg_dic['username']))
        self.assertEqual(False, server.member_manager.is_registered_nickname(user_reg_dic['nickname']))
        self.assertEqual(False, server.member_manager.is_registered_email(user_reg_dic['email']))

        # Register the user, login, and check if any problem occurs
        register_key = server.member_manager.register(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'mikkang', register_key)
        session_key = server.login_manager.login(u'mikkang', u'mikkang', u'143.248.234.140')
        server.login_manager.logout(session_key)

    def testNotAddSerialx(self):
        # XXX(combacsa): Implement Later
        pass

    def testViewCombacsa(self):
        session_key = server.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        member = server.member_manager.get_info(unicode(session_key))
        self.assertEqual(True, member.activated)
        self.assertEqual(u"combacsa@example.com", member.email)
        self.assertEqual(u"combacsa", member.nickname)
        self.assertEqual(0, member.widget)
        self.assertEqual(0, member.layout)
        server.login_manager.logout(session_key)

    def testPasswdChange(self):
        # Change password, and then login again to check it applied
        session_key = server.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        user_password_dic = {'username':u'combacsa', 'current_password':u'combacsa', 'new_password':u'computer'}
        server.member_manager.modify_password(session_key, UserPasswordInfo(**user_password_dic))
        server.login_manager.logout(session_key)
        try:
            session_key = server.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
            fail()
        except InvalidOperation:
            pass
        session_key = server.login_manager.login(u'combacsa', u'computer', u'143.248.234.145')
        # Change password again to let it be untouched
        user_password_dic = {'username':u'combacsa', 'current_password':u'computer', 'new_password':u'combacsa'}
        server.member_manager.modify_password(session_key, UserPasswordInfo(**user_password_dic))
        server.login_manager.logout(session_key)

    def testModifyInfo(self):
        session_key = server.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        modify_user_reg_dic = { 'nickname':u'combacsa is sysop', 'signature':u'KAIST07 && HSHS07 && SPARCS07', 'self_introduction':u'i am Kyuhong', 'default_language':u'korean', 'widget':1, 'layout':u'aaa' }
        server.member_manager.modify(session_key, UserModification(**modify_user_reg_dic))
        member = server.member_manager.get_info(unicode(session_key))
        self.assertEqual(1, member.widget)
        self.assertEqual(u"aaa", member.layout)
        self.assertEqual(u"combacsa is sysop", member.nickname)
        self.assertEqual(u"KAIST07 && HSHS07 && SPARCS07", member.signature)
        self.assertEqual(u"i am Kyuhong", member.self_introduction)
        self.assertEqual(u"korean", member.default_language)
        # Restore change (at least nickname)
        modify_user_reg_dic = { 'nickname':u'combacsa', 'signature':u'KAIST07 && HSHS07 && SPARCS07', 'self_introduction':u'i am Kyuhong', 'default_language':u'korean', 'widget':1, 'layout':u'aaa' }

        server.login_manager.logout(session_key)

    def testSearch(self):
        # Single User Result
        session_key = server.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        users = server.member_manager.search_user(session_key, u'serialx')
        self.assertEqual(1, len(users))
        self.assertEqual(u"serialx", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)
        # Multi User Result (Add new user with duplicated nickname)
        user_reg_dic = {'username':u'ggingkkang', 'password':u'xx', 'nickname':u'serialx', 'email':u'ggingkkang@example.com', 'signature':u'', 'self_introduction':u'', 'default_language':u'english' }
        register_key = server.member_manager.register(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'ggingkkang', unicode(register_key))

        users = server.member_manager.search_user(session_key, u'serialx')
        self.assertEqual(2, len(users))
        if (users[0].username == 'serialx'): # not sure about order
            self.assertEqual(u"serialx", users[0].username)
            self.assertEqual(u"serialx", users[0].nickname)
            self.assertEqual(u"ggingkkang", users[1].username)
            self.assertEqual(u"serialx", users[1].nickname)
        else:
            self.assertEqual(u"serialx", users[1].username)
            self.assertEqual(u"serialx", users[1].nickname)
            self.assertEqual(u"ggingkkang", users[0].username)
            self.assertEqual(u"serialx", users[0].nickname)

        users = server.member_manager.search_user(session_key, u'ggingkkang', u'username')
        self.assertEqual(1, len(users))
        self.assertEqual(u"ggingkkang", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)

        users = server.member_manager.search_user(session_key, u'combacsa', u'nickname')
        self.assertEqual(1, len(users))
        self.assertEqual(u"combacsa", users[0].username)
        self.assertEqual(u"combacsa", users[0].nickname)

        try:
            server.member_manager.search_user(session_key, u'mikkang', u'wrong_key')
            fail()
        except InvalidOperation:
            pass
        server.login_manager.logout(session_key)

        # 찾는 사람이 없는 경우에는?

    def testRemove(self):
        # XXX(serialx): User remove temp. removed.
        session_key = server.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        try:
            server.member_manager.remove_user(session_key)
            fail()
        except InvalidOperation:
            pass

    def testSysop(self):
        session_key = server.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        self.assertEqual(False, server.member_manager.is_sysop(session_key))
        server.login_manager.logout(session_key)
        session_key = server.login_manager.login(u'SYSOP', u'SYSOP', u'143.248.234.145')
        self.assertEqual(True, server.member_manager.is_sysop(session_key))
        server.login_manager.logout(session_key)
        # Prevent adding SYSOP
        user_reg_dic = { 'username':u'SYSOP', 'password':u'SYSOP', 'nickname':u'SYSOP', 'email':u'SYSOP@sparcs.org', 'signature':u'', 'self_introduction':u'i am mikkang', 'default_language':u'english' }
        try:
            sysop_register_key = server.member_manager.register(UserRegistration(**user_reg_dic))
            fail()
        except InvalidOperation:
            pass

    def testBackdoorConfirm(self):
        user_reg_dic = {'username':u'mikkang20', 'password':u'mikkang', 'nickname':u'mikkang20', 'email':u'mikkang20@example.com', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english' }
        registration_key = server.member_manager.register(UserRegistration(**user_reg_dic))
        session_key = server.login_manager.login(u'SYSOP', u'SYSOP', u'143.248.234.145')
        server.member_manager.backdoor_confirm(session_key, u'mikkang20')
        server.login_manager.logout(session_key)
        session_key = server.login_manager.login(u'mikkang20', u'mikkang', u'143.248.234.140')
        server.login_manager.logout(session_key)
        # XXX 시삽이 아닌 사람이 백도어 컨펌을 못 하는 것을 테스트.

    def tearDown(self):
        arara.model.clear_test_database()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MemberManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
