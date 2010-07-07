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

import time

class Test(unittest.TestCase):
    def _get_user_reg_dic(self, id):
        return {'username':id, 'password':id, 'nickname':id, 'email':id + u'@example.com',
                'signature':id, 'self_introduction':id, 'default_language':u'english', 'campus':u''}

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

        # Register two users
        self._register_user('pipoket')
        self._register_user('mikkang')

        # Login

        self.session_key_sysop = server.login_manager.login(u"SYSOP", u"SYSOP", u"123.123.123.123")
        self.session_key_pipoket = server.login_manager.login(u"pipoket", u"pipoket", u"123.123.123.123")
        self.session_key_mikkang = server.login_manager.login(u"mikkang", u"mikkang", u"123.123.123.123")

        # Add two board
        server.board_manager.add_board(self.session_key_sysop, u"search1", u"search1")
        server.board_manager.add_board(self.session_key_sysop, u"search2", u"search2")

    def tearDown(self):
        arara.model.clear_test_database()
        # Restore the time
        time.time = self.org_time

    def _dummy_article_write(self, session_key, board, title_append = u""):
        article_dic = {'title': u'TITLE' + title_append, 'content': u'CONTENT', 'heading': u''}
        return server.article_manager.write_article(session_key, board, Article(**article_dic))

    def test_search(self):
        # Scenario: pipoket write an article on search1 board.
        #           then mikkang search for that article.

        self._dummy_article_write(self.session_key_pipoket, u"search1")
        self._dummy_article_write(self.session_key_mikkang, u"search1")
        self._dummy_article_write(self.session_key_pipoket, u"search1")
        self._dummy_article_write(self.session_key_pipoket, u"search1")
        self._dummy_article_write(self.session_key_mikkang, u"search1")
        self._dummy_article_write(self.session_key_pipoket, u"search1")
        self._dummy_article_write(self.session_key_mikkang, u"search1")
        self._dummy_article_write(self.session_key_mikkang, u"search1")

        a = [x.id for x in server.search_manager.search(self.session_key_mikkang, True, u'search1', SearchQuery(**{'query': u'pipoket'}), 1, 20).hit]
        self.assertEqual([6, 4, 3, 1], a)

        b = [x.id for x in server.search_manager.search(self.session_key_pipoket, True, u'search1', SearchQuery(**{'query': u'mikkang'}), 1, 20).hit]
        self.assertEqual([8, 7, 5, 2], b)

        c = [x.id for x in server.search_manager.search(self.session_key_mikkang, True, u'search2', SearchQuery(**{'query': u'pipoket'}), 1, 20).hit]
        self.assertEqual([], c)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(Test)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
