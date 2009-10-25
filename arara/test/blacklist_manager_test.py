#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import logging

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(ARARA_PATH)

from arara_thrift.ttypes import *
import arara.model
import arara
import arara.server
import arara.model
server = None

# Time is needed for testing blacklist_manager
import time

class BlacklistManagerTest(unittest.TestCase):
    def setUp(self):
        global server
        # Common preparation for all tests
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        arara.server.server = arara.get_namespace()
        server = arara.get_namespace()

        # Fake time for further test
        def stub_time():
            return 1.1
        self.org_time = time.time
        time.time = stub_time

        # Register mikkang for test
        user_reg_dict = {'username':u'mikkang', 'password':u'mikkang', 
                        'nickname':u'mikkang', 'email':u'mikkang@example.com',
                        'signature':u'mikkang', 'self_introduction':u'mikkang',
                        'default_language':u'english' }
        register_key = server.member_manager.register(
                UserRegistration(**user_reg_dict))
        server.member_manager.confirm(u'mikkang', unicode(register_key))
        self.mikkang_session_key = server.login_manager.login(
                u'mikkang', u'mikkang', u'143.248.234.140')
        
        # Register combacsa for test
        user_reg_dic = {'username':u'combacsa', 'password':u'combacsa', 
                        'nickname':u'combacsa', 'email':u'combacsa@example.com', 
                        'signature':u'combacsa', 'self_introduction':u'combacsa', 
                        'default_language':u'english' }
        register_key = server.member_manager.register(
                UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'combacsa', register_key)
        self.combacsa_session_key = server.login_manager.login(
                 u'combacsa', u'combacsa', '143.248.234.140')

        # Register serialx for test 
        user_reg_dic = {'username':u'serialx', 'password':u'serialx', 
                        'nickname':u'serialx', 'email':u'serialx@example.com', 
                        'signature':u'serialx', 'self_introduction':u'serialx',
                        'default_language':u'english' }
        register_key = server.member_manager.register(
                UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'serialx', register_key)
        self.serialx_session_key = server.login_manager.login(
                u'serialx', u'serialx', u'143.248.234.140')

    def add(self):
        server.blacklist_manager.add(self.mikkang_session_key, u'combacsa')
        try:
            server.blacklist_manager.add(self.mikkang_session_key, u'pv457')
            fail()
        except InvalidOperation:
            pass
        try:
            server.blacklist_manager.add(self.mikkang_session_key, u'combacsa')
            fail()
        except InvalidOperation:  
            pass
        try:
            server.blacklist_manager.add(self.mikkang_session_key, u'mikkang')
            fail()
        except InvalidOperation:
            pass

        ret = server.blacklist_manager.list_(self.mikkang_session_key)[0]
        self.assertEqual(ret.blacklisted_user_nickname, u'combacsa')
        self.assertEqual(ret.last_modified_date, 1.1000000000000001)
        self.assertEqual(ret.block_article, True)
        self.assertEqual(ret.blacklisted_user_username, u'combacsa')
        self.assertEqual(ret.block_message, True)
        self.assertEqual(ret.blacklisted_date, 1.1000000000000001)
        self.assertEqual(ret.id, 1)

    def modify(self):
        blacklist_dict = {'blacklisted_user_username': u'combacsa', 
                          'block_article': False, 'block_message': True}
        server.blacklist_manager.modify(self.mikkang_session_key, 
                BlacklistRequest(**blacklist_dict))

        ret = server.blacklist_manager.list_(self.mikkang_session_key)[0]
        self.assertEqual(ret.blacklisted_user_nickname, u'combacsa')
        self.assertEqual(ret.last_modified_date, 1.1000000000000001)
        self.assertEqual(ret.block_article, False)
        self.assertEqual(ret.blacklisted_user_username, u'combacsa')
        self.assertEqual(ret.block_message, True)
        self.assertEqual(ret.blacklisted_date, 1.1000000000000001)
        self.assertEqual(ret.id, 1)
        
        try:
            blacklist_dict = {'blacklisted_user_username': u'pv457',
                              'block_article': False, 'block_message': True}
            server.blacklist_manager.modify(self.mikkang_session_key,
                    BlacklistRequest(**blacklist_dict))
            fail()
        except InvalidOperation:
            pass

    def delete(self):
        server.blacklist_manager.delete_(self.mikkang_session_key, u'combacsa')
        blacklist_dict = {'blacklisted_user_username': u'combacsa',
                          'block_article': False, 'block_message': True}
        try:
            server.blacklist_manager.modify(self.mikkang_session_key, 
                    BlacklistRequest(**blacklist_dict))
            fail()
        except InvalidOperation:
            pass
        try:
            server.blacklist_manager.delete_(self.mikkang_session_key, u'combacsa')
            fail()
        except InvalidOperation:
            pass
        try:
            server.blacklist_manager.delete_(self.mikkang_session_key, u'pv457')
            fail()
        except InvalidOperation:
            pass

    def test_add(self):
        self.add()

    def test_modify(self):
        self.add()
        self.modify()

    def test_delete(self):
        self.add()
        self.delete()

    def tearDown(self):
        arara.model.clear_test_database()
        time.time = self.org_time

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BlacklistManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
