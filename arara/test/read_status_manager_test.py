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

# Time is needed for testing file_manager
import time

class ReadStatusManagerTest(unittest.TestCase):
    def _get_user_reg_dic(self, id):
        return {'username':id, 'password':id, 'nickname':id, 
                'email':id + u'@example.com', 'signature':id,
                'self_introduction':id, 'default_language':u'english', 'campus':u''}

    def _register_user(self, id):
        # Register a user, log-in, and then return its session_key
        user_reg_dic = self._get_user_reg_dic(id)
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(id, unicode(register_key))
        return self.engine.login_manager.login(id, id, u'143.248.234.140')

    def setUp(self):
        # Common preparation for all tests
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = False
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        self.engine = arara_engine.ARAraEngine()

        # Fake time for further test
        def stub_time():
            return 1.1
        self.org_time = time.time
        time.time = stub_time

        # Login as SYSOP and create 'garbage'
        session_key_sysop = self.engine.login_manager.login(
                u'SYSOP', u'SYSOP', u'123.123.123.123')
        self.engine.board_manager.add_board(
                unicode(session_key_sysop), u'garbages', u'Garbage Board')
       
        # Register one user, mikkang
        self.session_key_mikkang = self._register_user(u'mikkang')

    def _write_articles(self):
        article = Article(**{'title': u'serialx is...', 'content': u'polarbear', 'heading': u''})
        self.engine.article_manager.write_article(
                self.session_key_mikkang, u'garbages', article)

        article = Article(**{'title': u'serialx is...', 'content': u'polarbear', 'heading': u''})
        self.engine.article_manager.write_article(
                self.session_key_mikkang, u'garbages', article)

    def tearDown(self):
        arara.model.clear_test_database()
        # Restore the time
        time.time = self.org_time
        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED
    def test_check_stat(self):
        self._write_articles()
        ret = self.engine.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("N", ret)

        try:
            self.engine.read_status_manager.check_stat(self.session_key_mikkang, 3)
            self.fail()
        except InvalidOperation:
            pass
        
        try:
            self.engine.read_status_manager.check_stat('asdfasdf', 1)
            self.fail()
        except NotLoggedIn:
            pass

    def test_check_stats(self):
        self._write_articles()
        ret = self.engine.read_status_manager.check_stats(
                self.session_key_mikkang, [1,2])
        self.assertEqual(["N", "N"], ret)

        try:
            self.engine.read_status_manager.check_stats(self.session_key_mikkang, [1,2,3])
            self.fail()
        except InvalidOperation:
            pass

        try:
            self.engine.read_status_manager.check_stats('asdfasdf', [1,2])
            self.fail()
        except NotLoggedIn:
            pass

    def test_mark_as_read(self):
        self._write_articles()
        ret = self.engine.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("N", ret)

        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 1)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 2)
        ret = self.engine.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("R", ret)
        ret = self.engine.read_status_manager.check_stat(
                self.session_key_mikkang, 2)
        self.assertEqual("R", ret)

        try:
            self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 3)
            self.fail()
        except InvalidOperation:
            pass

        try:
            self.engine.read_status_manager.mark_as_read('asdfasdf', 1)
            self.fail()
        except NotLoggedIn:
            pass

    def test_mark_as_viewed(self):
        self._write_articles()
        ret = self.engine.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("N", ret)

        self.engine.read_status_manager.mark_as_viewed(self.session_key_mikkang, 1)
        self.engine.read_status_manager.mark_as_viewed(self.session_key_mikkang, 2)
        ret = self.engine.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("V", ret)
        ret = self.engine.read_status_manager.check_stat(
                self.session_key_mikkang, 2)
        self.assertEqual("V", ret)

        try:
            self.engine.read_status_manager.mark_as_viewed(self.session_key_mikkang, 3)
            self.fail()
        except InvalidOperation:
            pass

        try:
            self.engine.read_status_manager.mark_as_viewed('asdfasdf', 1)
            self.fail()
        except NotLoggedIn:
            pass


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ReadStatusManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
