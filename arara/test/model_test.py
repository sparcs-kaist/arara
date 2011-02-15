#-*- coding: utf-8 -*-
# XXX combacsa: is this test really necessary?
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
from arara import arara_engine
import arara.model
import etc.arara_settings

import time
def stub_time():
    return 1.1


class ModelTest(unittest.TestCase):
    def setUp(self):
        # Common preparation for all tests
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = False
        logging.basicConfig(leve=logging.ERROR)
        arara.model.init_test_database()
        self.engine = arara_engine.ARAraEngine()
        # Faking time
        self.org_time = time.time
        time.time = stub_time
        # Create default board (garbages)
        session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', '123.123.123.123')
        self.engine.board_manager.add_board(session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'Garbage Board')
        # Register one user, serialx
        user_reg_dic = {'username':u'serialx', 'password':u'serialx', 'nickname':u'serialx', 'email':u'serialx@kaist.ac.kr', 'signature':u'serialx', 'self_introduction':u'serialx', 'default_language':u'english', 'campus':u'' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'serialx', register_key)
        # Up to here.
        self.engine.login_manager.logout(session_key_sysop)

    def testArticleWriteAndRead(self):
        """
        Heading 없이 글을 쓰고 읽는 것을 테스트한다.
        """
        session = arara.model.Session()
        board = session.query(arara.model.Board).filter_by(board_name=u'garbages').one()
        serialx = session.query(arara.model.User).filter_by(username=u'serialx').one()
        a = arara.model.Article(board, None, u'title1', u'content', serialx, u'0.0.0.0', None)
        b = arara.model.Article(board, None, u'title2', u'content', serialx, u'0.0.0.0', a)
        c = arara.model.Article(board, None, u'title3', u'content', serialx, u'0.0.0.0', b)
        d = arara.model.Article(board, None, u'title4', u'content', serialx, u'0.0.0.0', c)
        session.add(a)
        session.add(b)
        session.add(c)
        session.add(d)
        session.commit()

        self.assertEqual(repr(d.root), "<Article('title1', 'serialx', 1970-01-01 09:00:01.100000)>")
        self.assertEqual(repr(d.parent), "<Article('title3', 'serialx', 1970-01-01 09:00:01.100000)>")
        self.assertEqual(repr(c.children), "[<Article('title4', 'serialx', 1970-01-01 09:00:01.100000)>]")
        self.assertEqual(3, len(a.descendants))
        self.assertEqual(repr(a.descendants[0]), "<Article('title2', 'serialx', 1970-01-01 09:00:01.100000)>")
        self.assertEqual(repr(a.descendants[1]), "<Article('title3', 'serialx', 1970-01-01 09:00:01.100000)>")
        self.assertEqual(repr(a.descendants[2]), "<Article('title4', 'serialx', 1970-01-01 09:00:01.100000)>")
        session.close()

        session = arara.model.Session()
        a = session.query(arara.model.Article).filter_by(title=u'title1').one()
        c = session.query(arara.model.Article).filter_by(title=u'title3').one()
        d = session.query(arara.model.Article).filter_by(title=u'title4').one()

        self.assertEqual(repr(d.root), "<Article('title1', 'serialx', 1970-01-01 09:00:01.100000)>")
        self.assertEqual(repr(d.parent), "<Article('title3', 'serialx', 1970-01-01 09:00:01.100000)>")
        self.assertEqual(repr(c.children), "[<Article('title4', 'serialx', 1970-01-01 09:00:01.100000)>]")
        self.assertEqual(3, len(a.descendants))
        self.assertEqual(repr(a.descendants[0]), "<Article('title2', 'serialx', 1970-01-01 09:00:01.100000)>")
        self.assertEqual(repr(a.descendants[1]), "<Article('title3', 'serialx', 1970-01-01 09:00:01.100000)>")
        self.assertEqual(repr(a.descendants[2]), "<Article('title4', 'serialx', 1970-01-01 09:00:01.100000)>")
        session.close()

    def tearDown(self):
        self.engine.shutdown()
        time.time = self.org_time
        arara.model.clear_test_database()
        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ModelTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
