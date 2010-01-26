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
import arara.server
import arara.model
server = None

# Time is needed for testing file_manager
import time

class ReadStatusManagerTest(unittest.TestCase):
    def _get_user_reg_dic(self, id):
        return {'username':id, 'password':id, 'nickname':id, 
                'email':id + u'@example.com', 'signature':id,
                'self_introduction':id, 'default_language':u'english'}

    def _register_user(self, id):
        # Register a user, log-in, and then return its session_key
        user_reg_dic = self._get_user_reg_dic(id)
        register_key = server.member_manager.register_(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(id, unicode(register_key))
        return server.login_manager.login(id, id, u'143.248.234.140')

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

        # Login as SYSOP and create 'garbage'
        session_key_sysop = server.login_manager.login(
                u'SYSOP', u'SYSOP', u'123.123.123.123')
        server.board_manager.add_board(
                unicode(session_key_sysop), u'garbages', u'Garbage Board')
       
        # Register one user, mikkang
        self.session_key_mikkang = self._register_user(u'mikkang')

    def _write_articles(self):
        article = Article(**{'title': u'serialx is...', 'content': u'polarbear'})
        server.article_manager.write_article(
                self.session_key_mikkang, u'garbages', article)

        article = Article(**{'title': u'serialx is...', 'content': u'polarbear'})
        server.article_manager.write_article(
                self.session_key_mikkang, u'garbages', article)

    def tearDown(self):
        arara.model.clear_test_database()
        # Restore the time
        time.time = self.org_time

    def test_check_stat(self):
        self._write_articles()
        ret = server.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("N", ret)

        try:
            server.read_status_manager.check_stat(self.session_key_mikkang, 3)
            self.fail()
        except InvalidOperation:
            pass
        
        try:
            server.read_status_manager.check_stat('asdfasdf', 1)
            self.fail()
        except NotLoggedIn:
            pass

    def test_check_stats(self):
        self._write_articles()
        ret = server.read_status_manager.check_stats(
                self.session_key_mikkang, [1,2])
        self.assertEqual(["N", "N"], ret)

        try:
            server.read_status_manager.check_stats(self.session_key_mikkang, [1,2,3])
            self.fail()
        except InvalidOperation:
            pass

        try:
            server.read_status_manager.check_stats('asdfasdf', [1,2])
            self.fail()
        except NotLoggedIn:
            pass

    def test_mark_as_read(self):
        self._write_articles()
        ret = server.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("N", ret)

        server.read_status_manager.mark_as_read(self.session_key_mikkang, 1)
        server.read_status_manager.mark_as_read(self.session_key_mikkang, 2)
        ret = server.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("R", ret)
        ret = server.read_status_manager.check_stat(
                self.session_key_mikkang, 2)
        self.assertEqual("R", ret)

        try:
            server.read_status_manager.mark_as_read(self.session_key_mikkang, 3)
            self.fail()
        except InvalidOperation:
            pass

        try:
            server.read_status_manager.mark_as_read('asdfasdf', 1)
            self.fail()
        except NotLoggedIn:
            pass

    def test_mark_as_viewed(self):
        self._write_articles()
        ret = server.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("N", ret)

        server.read_status_manager.mark_as_viewed(self.session_key_mikkang, 1)
        server.read_status_manager.mark_as_viewed(self.session_key_mikkang, 2)
        ret = server.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("V", ret)
        ret = server.read_status_manager.check_stat(
                self.session_key_mikkang, 2)
        self.assertEqual("V", ret)

        try:
            server.read_status_manager.mark_as_viewed(self.session_key_mikkang, 3)
            self.fail()
        except InvalidOperation:
            pass

        try:
            server.read_status_manager.mark_as_viewed('asdfasdf', 1)
            self.fail()
        except NotLoggedIn:
            pass


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ReadStatusManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
