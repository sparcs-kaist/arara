#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import time

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara.test.test_common import AraraTestBase
from arara_thrift.ttypes import *
import arara.model


class MessagingManagerTest(AraraTestBase):
    def setUp(self):
        # Common preparation for all tests
        super(MessagingManagerTest, self).setUp(stub_time=True, stub_time_initial=1.1)

        # Register mikkang for test
        self.mikkang_session_key = self.register_and_login(u"mikkang")

        # Register combacsa for test
        self.combacsa_session_key = self.register_and_login(u"combacsa")

        # Register serialx for test
        self.serialx_session_key = self.register_and_login(u"serialx")

        # Register dodo for test
        self.zzongaly_session_key = self.register_and_login(u"zzongaly", default_user_reg_dic={u"nickname": u"dodo"})

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

    def test_get_unread_message_count(self):
        # 처음엔 한 통도 받은 메시지가 없다
        self.assertEqual(0, self.engine.messaging_manager.get_unread_message_count(self.mikkang_session_key))

        # serialx 가 mikkang 에게 메시지를 보낸다.
        # serialx 는 받은 메시지가 없지만 mikkang 이 받은 건 있게 됨.
        self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello')
        self.assertEqual(0, self.engine.messaging_manager.get_unread_message_count(self.serialx_session_key))
        self.assertEqual(1, self.engine.messaging_manager.get_unread_message_count(self.mikkang_session_key))

        # serialx 가 mikkang 에게 한통 더 메시지를 보낸다.
        # mikkang 이 받은 메시지만 한 통 증가한다.
        self.engine.messaging_manager.send_message(self.serialx_session_key, u'mikkang', u'hello2')
        self.assertEqual(0, self.engine.messaging_manager.get_unread_message_count(self.serialx_session_key))
        self.assertEqual(2, self.engine.messaging_manager.get_unread_message_count(self.mikkang_session_key))

        # mikkang 이 메시지를 한 통 읽는다
        self.engine.messaging_manager.read_received_message(self.mikkang_session_key, 1)
        self.assertEqual(1, self.engine.messaging_manager.get_unread_message_count(self.mikkang_session_key))

        # 이미 읽은 메시지를 읽는다고 unread message count 가 줄어들지는 않는다.
        self.engine.messaging_manager.read_received_message(self.mikkang_session_key, 1)
        self.assertEqual(1, self.engine.messaging_manager.get_unread_message_count(self.mikkang_session_key))

        # 아직 안 읽은 메시지를 읽으면 마저 줄어든다.
        self.engine.messaging_manager.read_received_message(self.mikkang_session_key, 2)
        self.assertEqual(0, self.engine.messaging_manager.get_unread_message_count(self.mikkang_session_key))

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


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessagingManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
