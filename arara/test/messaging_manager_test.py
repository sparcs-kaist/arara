#-*- coding: utf:-8 -*-
import unittest
import os
import sys

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara_thrift.ttypes import *
import arara.model
import arara
import arara.server
import arara.model
server = None

# Time is needed for testing file_manager
import time

class MessagingMangaerTest(unittest.TestCase):
    def setUp(self):
        global server
        # Common preparation for all tests
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
        server.member_manager.confirm(u'combacsa', unicode(register_key))
        self.combacsa_session_key = server.login_manager.login(
                u'combacsa', u'combacsa', '143.248.234.140')

        # Register serialx for test
        user_reg_dic = {'username':u'serialx', 'password':u'serialx',
                'nickname':u'serialx', 'email':u'serialx@example.com', 
                'signature':u'serialx', 'self_introduction':u'serialx', 
                'default_language':u'english' }
        register_key = server.member_manager.register(
                UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'serialx', unicode(register_key))
       self.serialx_session_key = server.login_manager.login(
                u'serialx', u'serialx', '143.248.234.140')

    def tearDown(self):
        arara.model.clear_test_database()
        # Restore the time
        time.time = self.org_time

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FileManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
