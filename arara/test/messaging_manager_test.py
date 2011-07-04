#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import logging

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara_thrift.ttypes import *
import arara.model
import arara
from arara import arara_engine
import arara.model
import etc.arara_settings
from arara.test.test_common import AraraTestBase

# Time is needed for testing file_manager
import time

class MessagingManagerTest(AraraTestBase):
    def setUp(self):
        # Common preparation for all tests
        super(MessagingManagerTest, self).setUp()

        # Fake time for further test
        def stub_time():
            return 1.1
        self.org_time = time.time
        time.time = stub_time

        # Register mikkang for test
        user_reg_dict = {'username':u'mikkang', 'password':u'mikkang', 
                        'nickname':u'mikkang', 'email':u'mikkang@kaist.ac.kr',
                        'signature':u'mikkang', 'self_introduction':u'mikkang',
                        'default_language':u'english', 'campus':u'Daejeon' }
        register_key = self.engine.member_manager.register_(
                UserRegistration(**user_reg_dict))
        self.engine.member_manager.confirm(u'mikkang', unicode(register_key))
        self.mikkang_session_key = self.engine.login_manager.login(
                u'mikkang', u'mikkang', u'143.248.234.140')
                
        # Register combacsa for test
        user_reg_dic = {'username':u'combacsa', 'password':u'combacsa',
                        'nickname':u'combacsa', 'email':u'combacsa@kaist.ac.kr',
                        'signature':u'combacsa', 'self_introduction':u'combacsa', 
                        'default_language':u'english', 'campus':u'Seoul' }
        register_key = self.engine.member_manager.register_(
                UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'combacsa', unicode(register_key))
        self.combacsa_session_key = self.engine.login_manager.login(
                u'combacsa', u'combacsa', '143.248.234.140')

        # Register serialx for test
        user_reg_dic = {'username':u'serialx', 'password':u'serialx',
                'nickname':u'serialx', 'email':u'serialx@kaist.ac.kr', 
                'signature':u'serialx', 'self_introduction':u'serialx', 
                'default_language':u'english', 'campus':u'' }
        register_key = self.engine.member_manager.register_(
                UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'serialx', unicode(register_key))
        self.serialx_session_key = self.engine.login_manager.login(
                u'serialx', u'serialx', '143.248.234.140')
        
        # Register dodo for test
        user_reg_dic = {'username':u'zzongaly', 'password':u'zzongaly', 
                'nickname':u'dodo', 'email':u'zzongaly@kaist.ac.kr', 
                'signature':u'mikkang friend', 'self_introduction':u'i am dodo', 
                'default_language':u'english', 'campus':u'' }
        register_key = self.engine.member_manager.register_(
                UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'zzongaly', unicode(register_key))
        self.zzongaly_session_key = self.engine.login_manager.login(
                u'zzongaly', u'zzongaly', '143.248.234.140')

    def test_sent_list(self):
        ret = self.engine.messaging_manager.sent_list(self.serialx_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 0)
        self.assertEqual(ret.new_message_count, 0)

        self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello1')
        ret = self.engine.messaging_manager.sent_list(self.serialx_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 1)
        self.assertEqual(ret.new_message_count, 0)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 1)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello1')
        self.assertEqual(msg.read_status, u'N')

        self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello2')
        ret = self.engine.messaging_manager.sent_list(self.serialx_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 2)
        self.assertEqual(ret.new_message_count, 0)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 2)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello2')
        self.assertEqual(msg.read_status, u'N')

        for i in range(10):
            self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello10')
        ret = self.engine.messaging_manager.sent_list(self.serialx_session_key, 1, 10)
        self.assertEqual(ret.last_page, 2)
        self.assertEqual(ret.results, 12)
        self.assertEqual(ret.new_message_count, 0)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 12)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello10')
        self.assertEqual(msg.read_status, u'N')

        ret = self.engine.messaging_manager.sent_list(self.serialx_session_key, 2, 10)
        self.assertEqual(ret.last_page, 2)
        self.assertEqual(ret.results, 12)
        self.assertEqual(ret.new_message_count, 0)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 2)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello2')
        self.assertEqual(msg.read_status, u'N')

        try:
            self.engine.messaging_manager.sent_list(u'strange_session')
            fail()
        except NotLoggedIn:
            pass

    def test_receive_list(self):
        ret = self.engine.messaging_manager.receive_list(self.mikkang_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 0)
        self.assertEqual(ret.new_message_count, 0)
        
        self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello')
        ret = self.engine.messaging_manager.receive_list(self.serialx_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 0)
        self.assertEqual(ret.new_message_count, 0)

        ret = self.engine.messaging_manager.receive_list(self.mikkang_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 1)
        self.assertEqual(ret.new_message_count, 1)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 1)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello')
        self.assertEqual(msg.read_status, u'N')

        self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello2')
        ret = self.engine.messaging_manager.receive_list(self.mikkang_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 2)
        self.assertEqual(ret.new_message_count, 2)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 2)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello2')
        self.assertEqual(msg.read_status, u'N')

    def test_send_message_by_username(self):
        self.engine.messaging_manager.send_message_by_username(self.mikkang_session_key, u'zzongaly', u'hi dodo username test')

        ret = self.engine.messaging_manager.receive_list(self.zzongaly_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 1)
        self.assertEqual(ret.new_message_count, 1)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 1)
        self.assertEqual(msg.from_nickname, u'mikkang')
        self.assertEqual(msg.from_, u'mikkang')
        self.assertEqual(msg.to_nickname, u'dodo')
        self.assertEqual(msg.to, u'zzongaly')
        self.assertEqual(msg.message, u'hi dodo username test')
        self.assertEqual(msg.read_status, u'N')

    def test_send_message_by_nickname(self):
        self.engine.messaging_manager.send_message_by_nickname(self.mikkang_session_key, u'dodo', u'hi dodo nickname test')

        ret = self.engine.messaging_manager.receive_list(self.zzongaly_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 1)
        self.assertEqual(ret.new_message_count, 1)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 1)
        self.assertEqual(msg.from_nickname, u'mikkang')
        self.assertEqual(msg.from_, u'mikkang')
        self.assertEqual(msg.to_nickname, u'dodo')
        self.assertEqual(msg.to, u'zzongaly')
        self.assertEqual(msg.message, u'hi dodo nickname test')
        self.assertEqual(msg.read_status, u'N')
        pass

    def test_send_message(self):
        for i in range(100):
            self.engine.messaging_manager.send_message(self.mikkang_session_key, u'serialx', unicode(i+1))

        msg = self.engine.messaging_manager.read_received_message(self.serialx_session_key, 92)
        self.assertEqual(msg.id , 92)
        self.assertEqual(msg.from_nickname, u'mikkang')
        self.assertEqual(msg.from_, u'mikkang')
        self.assertEqual(msg.to_nickname, u'serialx')
        self.assertEqual(msg.to, u'serialx')
        self.assertEqual(msg.message, u'92')
        self.assertEqual(msg.read_status, u'N')

        ret = self.engine.messaging_manager.receive_list(self.serialx_session_key, 1, 10)
        self.assertEqual(ret.last_page, 10)
        self.assertEqual(ret.results, 100)
        self.assertEqual(ret.new_message_count, 99)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 100)
        self.assertEqual(msg.from_nickname, u'mikkang')
        self.assertEqual(msg.from_, u'mikkang')
        self.assertEqual(msg.to_nickname, u'serialx')
        self.assertEqual(msg.to, u'serialx')
        self.assertEqual(msg.message, u'100')
        self.assertEqual(msg.read_status, u'N')

        ret = self.engine.messaging_manager.receive_list(self.serialx_session_key, 10, 10)
        self.assertEqual(ret.last_page, 10)
        self.assertEqual(ret.results, 100)
        self.assertEqual(ret.new_message_count, 99)
        msg = ret.hit[0]
        self.assertEqual(msg.id , 10)
        self.assertEqual(msg.from_nickname, u'mikkang')
        self.assertEqual(msg.from_, u'mikkang')
        self.assertEqual(msg.to_nickname, u'serialx')
        self.assertEqual(msg.to, u'serialx')
        self.assertEqual(msg.message, u'10')
        self.assertEqual(msg.read_status, u'N')
        msg = ret.hit[9]
        self.assertEqual(msg.id , 1)
        self.assertEqual(msg.from_nickname, u'mikkang')
        self.assertEqual(msg.from_, u'mikkang')
        self.assertEqual(msg.to_nickname, u'serialx')
        self.assertEqual(msg.to, u'serialx')
        self.assertEqual(msg.message, u'1')
        self.assertEqual(msg.read_status, u'N')

        try:
            self.engine.messaging_manager.send_message(u'strange_session', u'mikkang', u'SPAM_SPAM!!!!')
            fail()
        except NotLoggedIn:
            pass

        try:
            self.engine.messaging_manager.send_message(self.serialx_session_key, u'non_exist', u'SPAM~')
            fail()
        except InvalidOperation:
            pass

    def test_read_received_message(self):
        for i in range(10):
            self.engine.messaging_manager.send_message(self.mikkang_session_key, u'serialx', unicode(i+1))

        msg = self.engine.messaging_manager.read_received_message(self.serialx_session_key, 5)
        self.assertEqual(msg.id , 5)
        self.assertEqual(msg.from_nickname, u'mikkang')
        self.assertEqual(msg.from_, u'mikkang')
        self.assertEqual(msg.to_nickname, u'serialx')
        self.assertEqual(msg.to, u'serialx')
        self.assertEqual(msg.message, u'5')
        self.assertEqual(msg.read_status, u'N')

        try:
            self.engine.messaging_manager.read_received_message(self.serialx_session_key, 12)
            fail()
        except InvalidOperation:
            pass

        try:
            self.engine.messaging_manager.read_received_message(u'starnge_session_key', 5)
            fail()
        except NotLoggedIn:
            pass

    def test_read_sent_message(self):
        self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello1')
        msg = self.engine.messaging_manager.read_sent_message(self.serialx_session_key, 1)
        self.assertEqual(msg.id , 1)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello1')
        self.assertEqual(msg.read_status, u'N')

        self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello2')
        msg = self.engine.messaging_manager.read_sent_message(self.serialx_session_key, 2)
        self.assertEqual(msg.id , 2)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello2')
        self.assertEqual(msg.read_status, u'N')


        for i in range(10):
            self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello10')

        msg = self.engine.messaging_manager.read_sent_message(self.serialx_session_key, 12)
        self.assertEqual(msg.id , 12)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello10')
        self.assertEqual(msg.read_status, u'N')

        try:
            self.engine.messaging_manager.read_sent_message(u'strange_session', 3)
            fail()
        except NotLoggedIn:
            pass

        try:
            self.engine.messaging_manager.read_sent_message(self.serialx_session_key, 99)
            fail()
        except InvalidOperation:
            pass

    def test_delete_received_message(self):
        for i in range(10):
            self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello%s' % (i+1))

        ret = self.engine.messaging_manager.receive_list(self.mikkang_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 10)
        self.assertEqual(ret.new_message_count, 10)
        self.engine.messaging_manager.read_received_message(self.mikkang_session_key, 2)
        msg = self.engine.messaging_manager.read_received_message(self.mikkang_session_key, 1)
        self.assertEqual(msg.id , 1)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello1')
        self.assertEqual(msg.read_status, u'N')

        self.engine.messaging_manager.delete_received_message(self.mikkang_session_key, 1)
        try:
            self.engine.messaging_manager.read_received_message(self.mikkang_session_key, 1)
            fail()
        except InvalidOperation:
            pass

        ret = self.engine.messaging_manager.receive_list(self.mikkang_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 9)
        self.assertEqual(ret.new_message_count, 8)

        try:
            self.engine.messaging_manager.delete_received_message(self.serialx_session_key, 99)
            fail()
        except InvalidOperation:
            pass

        try:
            self.engine.messaging_manager.delete_received_message(u'starnge_session', 2)
            fail()
        except NotLoggedIn:
            pass

    def test_delete_sent_message(self):
        for i in range(10):
            self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello%s' % (i+1))

        ret = self.engine.messaging_manager.sent_list(self.serialx_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 10)
        self.assertEqual(ret.new_message_count, 0)
        msg = self.engine.messaging_manager.read_sent_message(self.serialx_session_key, 1)
        self.assertEqual(msg.id , 1)
        self.assertEqual(msg.from_nickname, u'serialx')
        self.assertEqual(msg.from_, u'serialx')
        self.assertEqual(msg.to_nickname, u'mikkang')
        self.assertEqual(msg.to, u'mikkang')
        self.assertEqual(msg.message, u'hello1')
        self.assertEqual(msg.read_status, u'N')

        self.engine.messaging_manager.delete_sent_message(self.serialx_session_key, 1)
        try:
            self.engine.messaging_manager.read_sent_message(self.serialx_session_key, 1)
            fail()
        except InvalidOperation:
            pass

        ret = self.engine.messaging_manager.sent_list(self.serialx_session_key)
        self.assertEqual(ret.last_page, 1)
        self.assertEqual(ret.results, 9)
        self.assertEqual(ret.new_message_count, 0)

        try:
            self.engine.messaging_manager.delete_sent_message(self.serialx_session_key, 99)
            fail()
        except InvalidOperation:
            pass

        try:
            self.engine.messaging_manager.delete_sent_message(u'starnge_session', 2)
            fail()
        except NotLoggedIn:
            pass

    def tearDown(self):
        # Common tearDown
        super(MessagingManagerTest, self).tearDown()

        # Restore the time
        time.time = self.org_time
        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessagingManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
