#-*- coding: utf:-8 -*-

import unittest
import os
import sys
import logging
import time

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(ARARA_PATH)

from arara_thrift.ttypes import *
import arara.model
import arara
import arara.model
from arara import arara_engine
import etc.arara_settings

STUB_TIME_INITIAL = 31536000.1
STUB_TIME_CURRENT = STUB_TIME_INITIAL

def stub_time():
    # XXX Not Thread-safe!
    global STUB_TIME_CURRENT
    return STUB_TIME_CURRENT

class NoticeManagerTest(unittest.TestCase):
    def setUp(self):
        # Common preparation for all tests
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = False
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        self.engine = arara_engine.ARAraEngine()

        # SYSOP으로 로그인
        self.session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', '143.234.234.234')

        # Faking time.time
        self.org_time = time.time
        time.time = stub_time
        STUB_TIME_CURRENT = STUB_TIME_INITIAL

    def testAddBanner(self):
        # 배너 하나를 추가한다
        notice_reg_dic = {'content' : u'/media/image/banner_1.png', 'due_date' : 31537001.100000001, 'weight' : 1}
        banner_1 = self.engine.notice_manager.add_banner(self.session_key_sysop, WrittenNotice(**notice_reg_dic)) 
        self.assertEqual(1, banner_1)
        # 배너가 추가되었는지 확인한다
        banner_list = self.engine.notice_manager.list_banner(self.session_key_sysop)
        expected_result = "[Notice(due_date=31537001.100000001, weight=1, issued_date=31536000.100000001, content=u'/media/image/banner_1.png', valid=False, id=1)]"
        self.assertEqual(1, len(banner_list))
        self.assertEqual(expected_result, repr(banner_list))
        # 배너를 하나 더 추가한다
        notice_reg_dic = {'content' : u'/media/image/banner_2.png', 'due_date' : 31636001.100000001, 'weight' : 3}
        banner_2 = self.engine.notice_manager.add_banner(self.session_key_sysop, WrittenNotice(**notice_reg_dic)) 
        self.assertEqual(2, banner_2)
        # 배너가 추가되었는지 확인한다
        banner_list = self.engine.notice_manager.list_banner(self.session_key_sysop)
        expected_result = "[Notice(due_date=31537001.100000001, weight=1, issued_date=31536000.100000001, content=u'/media/image/banner_1.png', valid=False, id=1), Notice(due_date=31636001.100000001, weight=3, issued_date=31536000.100000001, content=u'/media/image/banner_2.png', valid=False, id=2)]"
        self.assertEqual(2, len(banner_list))
        self.assertEqual(expected_result, repr(banner_list))

    def tearDown(self):
        arara.model.clear_test_database()
        time.time = self.org_time

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NoticeManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
