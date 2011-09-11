#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import time

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(ARARA_PATH)

from arara.test.test_common import AraraTestBase
from arara_thrift.ttypes import *
import arara.model


class BlacklistManagerTest(AraraTestBase):
    def setUp(self):
        # Common preparation for all tests
        super(BlacklistManagerTest, self).setUp()

        # Fake time for further test
        def stub_time():
            return 1.1
        self.org_time = time.time
        time.time = stub_time

        # Register mikkang for test
        self.mikkang_session_key = self.register_and_login(u'mikkang')
        
        # Register combacsa for test
        self.combacsa_session_key = self.register_and_login(u'combacsa')

        # Register serialx for test 
        self.serialx_session_key = self.register_and_login(u'serialx')

    def test_add(self):
        self.engine.blacklist_manager.add_blacklist(self.mikkang_session_key, u'combacsa')
        # Case 0. 정상 작동
        ret = self.engine.blacklist_manager.get_blacklist(self.mikkang_session_key)[0]
        self.assertEqual(ret.blacklisted_user_nickname, u'combacsa')
        self.assertEqual(ret.last_modified_date, 1.1000000000000001)
        self.assertEqual(ret.block_article, True)
        self.assertEqual(ret.blacklisted_user_username, u'combacsa')
        self.assertEqual(ret.block_message, True)
        self.assertEqual(ret.blacklisted_date, 1.1000000000000001)
        self.assertEqual(ret.id, 1)

        # Case 1. 존재하지 않는 유저
        try:
            self.engine.blacklist_manager.add_blacklist(self.mikkang_session_key, u'pv457')
            self.fail()
        except InvalidOperation:
            pass
        # Case 2. 이미 등록한 유저
        try:
            self.engine.blacklist_manager.add_blacklist(self.mikkang_session_key, u'combacsa')
            self.fail()
        except InvalidOperation:  
            pass
        # Case 3. 자기 자신
        try:
            self.engine.blacklist_manager.add_blacklist(self.mikkang_session_key, u'mikkang')
            self.fail()
        except InvalidOperation:
            pass

    def test_modify(self):
        # Setting.
        self.engine.blacklist_manager.add_blacklist(self.mikkang_session_key, u'combacsa')
        # Case 1. 수정 잘 되는지 확인
        blacklist_dict = {'blacklisted_user_username': u'combacsa', 
                          'block_article': False, 'block_message': True}
        self.engine.blacklist_manager.modify_blacklist(self.mikkang_session_key, 
                BlacklistRequest(**blacklist_dict))

        ret = self.engine.blacklist_manager.get_blacklist(self.mikkang_session_key)[0]
        self.assertEqual(ret.blacklisted_user_nickname, u'combacsa')
        self.assertEqual(ret.last_modified_date, 1.1000000000000001)
        self.assertEqual(ret.block_article, False)
        self.assertEqual(ret.blacklisted_user_username, u'combacsa')
        self.assertEqual(ret.block_message, True)
        self.assertEqual(ret.blacklisted_date, 1.1000000000000001)
        self.assertEqual(ret.id, 1)
        # Case 2. Blacklist 에 없는 사용자 추가 실패
        try:
            blacklist_dict = {'blacklisted_user_username': u'pv457',
                              'block_article': False, 'block_message': True}
            self.engine.blacklist_manager.modify_blacklist(self.mikkang_session_key,
                    BlacklistRequest(**blacklist_dict))
            self.fail()
        except InvalidOperation:
            pass

    def test_delete(self):
        # Setting.
        self.engine.blacklist_manager.add_blacklist(self.mikkang_session_key, u'combacsa')
        # Case 1. 정상 삭제
        self.engine.blacklist_manager.delete_blacklist(self.mikkang_session_key, u'combacsa')
        # Case 2. 정상 삭제 후 수정 실패
        blacklist_dict = {'blacklisted_user_username': u'combacsa',
                          'block_article': False, 'block_message': True}
        try:
            self.engine.blacklist_manager.modify_blacklist(self.mikkang_session_key, 
                    BlacklistRequest(**blacklist_dict))
            self.fail()
        except InvalidOperation:
            pass
        # Case 3. 정상 삭제 후 다시 삭제 실패
        try:
            self.engine.blacklist_manager.delete_blacklist(self.mikkang_session_key, u'combacsa')
            self.fail()
        except InvalidOperation:
            pass
        # Case 4. 존재하지 않는 유저 삭제 실패
        try:
            self.engine.blacklist_manager.delete_blacklist(self.mikkang_session_key, u'pv457')
            self.fail()
        except InvalidOperation:
            pass

    def test_get_article_blacklisted_userid_list(self):
        # Setting.
        self.engine.blacklist_manager.add_blacklist(self.mikkang_session_key, u'combacsa')
        self.engine.blacklist_manager.add_blacklist(self.mikkang_session_key, u'serialx')
        # Case 1. 정상 작동
        result = self.engine.blacklist_manager.get_article_blacklisted_userid_list(self.mikkang_session_key)
        self.assertEqual([3, 4], result)
        # Case 1-1. serialx 를 지우고 get 할 때 combacsa 만 돌아오는가
        self.engine.blacklist_manager.delete_blacklist(self.mikkang_session_key, u'serialx')
        result = self.engine.blacklist_manager.get_article_blacklisted_userid_list(self.mikkang_session_key)
        self.assertEqual([3], result)
        # TODO : 없는 유저에 대해 작동 안하는 거 확인.

    def tearDown(self):
        # Common tearDown
        super(BlacklistManagerTest, self).tearDown()

        # restore time.time
        time.time = self.org_time

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BlacklistManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
