#-*- coding: utf-8 -*-
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
import arara.server
import arara.model
import time
server = None

STUB_TIME_INITIAL = 31536000.1
STUB_TIME_CURRENT = STUB_TIME_INITIAL

def stub_time():
    # XXX Not Thread-safe!
    global STUB_TIME_CURRENT
    return STUB_TIME_CURRENT

class ArticleManagerTest(unittest.TestCase):
    def _get_user_reg_dic(self, id):
        return {'username':id, 'password':id, 'nickname':id, 'email':id + u'@example.com',
                'signature':id, 'self_introduction':id, 'default_language':u'english'}

    def _register_user(self, id):
        # Register a user, log-in, and then return its session_key
        user_reg_dic = self._get_user_reg_dic(id)
        register_key = server.member_manager.register_(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(id, unicode(register_key))
        return server.login_manager.login(id, id, u'143.248.234.140')

    def setUp(self):
        global server
        global STUB_TIME_CURRENT
        # Common preparation for all tests
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        arara.server.server = arara.get_namespace()
        server = arara.get_namespace()
        # SYSOP will appear.
        self.session_key_sysop = server.login_manager.login(u'SYSOP', u'SYSOP', u'123.123.123.123')
        # Faking time.time
        self.org_time = time.time
        time.time = stub_time
        STUB_TIME_CURRENT = STUB_TIME_INITIAL
        # Register mikkang, serialx
        self.session_key_mikkang = self._register_user(u'mikkang')
        self.session_key_serialx = self._register_user(u'serialx')
        # Create default board
        server.board_manager.add_board(self.session_key_sysop, u'board', u'Test Board')

    def tearDown(self):
        arara.model.clear_test_database()
        time.time = self.org_time

    def test_read_only_board(self):
        # Add a read-only board. Try to write an article. Must fail.
        server.board_manager.add_read_only_board(self.session_key_sysop, u'board')

        article = Article(**{'title': u'serialx is...', 'content': u'polarbear'})
        try:
            server.article_manager.write_article(self.session_key_sysop, u'board', article)
            self.fail()
        except InvalidOperation:
            pass

    def _dummy_article_write(self, session_key, title_append = u""):
        global STUB_TIME_CURRENT
        STUB_TIME_CURRENT += 1.0
        article_dic = {'title': u'TITLE' + title_append, 'content': u'CONTENT'}
        return server.article_manager.write_article(session_key, u'board', Article(**article_dic))

    def test_write_and_read_basic(self):
        # Write an article.
        article_id = self._dummy_article_write(self.session_key_mikkang)
        # Checking the article id, then read, and check the contents.
        self.assertEqual(1, article_id)
        expected_result = "[Article(attach=None, board_name=None, author_username=u'mikkang', hit=1, blacklisted=False, title=u'TITLE', deleted=False, read_status=None, root_id=1, is_searchable=True, author_nickname=u'mikkang', content=u'CONTENT', vote=0, depth=1, reply_count=None, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type=None, id=1)]"
        self.assertEqual(expected_result, repr(server.article_manager.read(self.session_key_mikkang, u'board', 1)))

    def test_reply(self):
        # Test fail to reply on a nonexisting article
        reply_dic = WrittenArticle(**{'title':u'dummy', 'content': u'asdf'})
        try:
            server.article_manager.write_reply(self.session_key_mikkang, u'board', 24, reply_dic)
            self.fail()
        except InvalidOperation:
            pass
        # Test successfully reply on an existing article.
        article_id = self._dummy_article_write(self.session_key_mikkang)
        global STUB_TIME_CURRENT
        STUB_TIME_CURRENT += 1.0
        reply_id   = server.article_manager.write_reply(self.session_key_mikkang, u'board', 1, reply_dic)
        self.assertEqual(2, reply_id)
        # Test read original article again.
        expected_result = "[Article(attach=None, board_name=None, author_username=u'mikkang', hit=1, blacklisted=False, title=u'TITLE', deleted=False, read_status=None, root_id=1, is_searchable=True, author_nickname=u'mikkang', content=u'CONTENT', vote=0, depth=1, reply_count=None, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type=None, id=1), Article(attach=None, board_name=None, author_username=u'mikkang', hit=0, blacklisted=False, title=u'dummy', deleted=False, read_status=None, root_id=1, is_searchable=True, author_nickname=u'mikkang', content=u'asdf', vote=0, depth=2, reply_count=None, last_modified_date=31536002.100000001, date=31536002.100000001, author_id=2, type=None, id=2)]"
        self.assertEqual(expected_result, repr(server.article_manager.read(self.session_key_mikkang, u'board', 1)))
        # List the article (should only be one article in the list
        # XXX It shouldn't be a repr!!! Please replace it.
        expected_result = "ArticleList(last_page=1, hit=[Article(attach=None, board_name=None, author_username=u'mikkang', hit=1, blacklisted=False, title=u'TITLE', deleted=False, read_status='R', root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=1, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type='normal', id=1)], results=1, current_page=None)"
        self.assertEqual(expected_result, repr(server.article_manager.article_list(self.session_key_mikkang, u'board')))

    def test_reply_changes_list(self):
        # Preparation
        article_1_id = self._dummy_article_write(self.session_key_mikkang)
        article_2_id = self._dummy_article_write(self.session_key_serialx)
        global STUB_TIME_CURRENT
        STUB_TIME_CURRENT += 1.0
        reply_dic    = WrittenArticle(**{'title':u'dummy', 'content': u'asdf'})
        reply_id     = server.article_manager.write_reply(self.session_key_mikkang, u'board', 1, reply_dic)
        # Without reply, listing order must be [article 2, article 1].
        # But since new reply was found on article 1, listing order must be [article 1, article 2].
        expected_result = "ArticleList(last_page=1, hit=[Article(attach=None, board_name=None, author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE', deleted=False, read_status='N', root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=1, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type='normal', id=1), Article(attach=None, board_name=None, author_username=u'serialx', hit=0, blacklisted=False, title=u'TITLE', deleted=False, read_status='N', root_id=None, is_searchable=True, author_nickname=u'serialx', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536002.100000001, date=31536002.100000001, author_id=3, type='normal', id=2)], results=2, current_page=None)"
        self.assertEqual(expected_result, repr(server.article_manager.article_list(self.session_key_mikkang, u'board')))

    def test_pagination(self):
        # Write some articles
        for i in range(1, 105):
            self._dummy_article_write(self.session_key_mikkang, unicode(i))
        # Check some articles
        l = server.article_manager.article_list(self.session_key_mikkang, u'board')
        self.assertEqual(u'TITLE104', l.hit[0].title)
        self.assertEqual(u'TITLE103', l.hit[1].title)
        self.assertEqual(u'TITLE85', l.hit[19].title)
        l = server.article_manager.article_list(self.session_key_mikkang, u'board', page=2)
        self.assertEqual(u'TITLE84', l.hit[0].title)
        self.assertEqual(6, l.last_page)

    def testReadStatus(self):
        # XXX : ReadStatusManager 가 잘 작동되어서 그 결과가
        #       ArticleManager 에 잘 반영되었는지 점검하는 것.

        # Write some articles
        article_id1 = self._dummy_article_write(self.session_key_mikkang)
        article_id2 = self._dummy_article_write(self.session_key_mikkang)
        article_id3 = self._dummy_article_write(self.session_key_mikkang)
        # Test that everything is New
        l = server.article_manager.article_list(self.session_key_serialx, u'board')
        self.assertEqual('N', l.hit[2].read_status)
        self.assertEqual('N', l.hit[1].read_status)
        self.assertEqual('N', l.hit[0].read_status)
        # Now Read some article and test if it is changed as read
        article_1 = server.article_manager.read(self.session_key_serialx, u'board', article_id3)
        article_2 = server.article_manager.read(self.session_key_serialx, u'board', article_id2)
        l = server.article_manager.article_list(self.session_key_serialx, u'board')
        self.assertEqual('N', l.hit[2].read_status)
        self.assertEqual('R', l.hit[1].read_status)
        self.assertEqual('R', l.hit[0].read_status)

    def test_deletion(self):
        # Write some articles
        article1_id = self._dummy_article_write(self.session_key_mikkang)
        article2_id = self._dummy_article_write(self.session_key_mikkang)
        article3_id = self._dummy_article_write(self.session_key_mikkang)
        # Delete these!
        self.assertEqual(True, server.article_manager.delete_(self.session_key_mikkang, u'board', article1_id))
        self.assertEqual(True, server.article_manager.read(self.session_key_mikkang, u'board', article1_id)[0].deleted)
        # XXX: Well.. It will be safe to check all the other information remain
        # Can't delete which not exist
        try:
            server.article_manager.delete_(self.session_key_mikkang, u'board', 1241252)
            self.fail()
        except InvalidOperation:
            pass
        # Can't delete which I didn't write
        try:
            server.article_manager.delete_(self.session_key_serialx, u'board', article2_id)
            self.fail()
        except InvalidOperation:
            pass
        # Can't delete which I already deleted
        try:
            server.article_manager.delete_(self.session_key_mikkang, u"board", article1_id)
            self.fail()
        except InvalidOperation:
            pass

    def test_destroy(self):
        # Write some articles
        article1_id = self._dummy_article_write(self.session_key_mikkang)
        article2_id = self._dummy_article_write(self.session_key_mikkang)
        article3_id = self._dummy_article_write(self.session_key_mikkang)
        # Delete one.
        server.article_manager.delete_(self.session_key_mikkang, u'board', article1_id)
        try:
            # Destroy one. Must fail, because delete automatically destroy article.
            self.assertEqual(True, server.article_manager.destroy_article(self.session_key_sysop, u'board', article1_id))
            self.fail()
        except InvalidOperation:
            pass
        # Can't destroy which do not exist.
        try:
            server.article_manager.destroy_article(self.session_key_sysop, u'board', 1241252)
            self.fail()
        except InvalidOperation:
            pass
        # Can't destroy someone other than sysop
        try:
            server.article_manager.destroy_article(self.session_key_mikkang, u'board', article2_id)
            self.fail()
        except InvalidOperation:
            pass
        # Can't destroy which already destroyed.
        try:
            server.article_manager.destroy_article(self.session_key_sysop, u"board", article1_id)
            self.fail()
        except InvalidOperation:
            pass
        # TODO : Check whether it is marked as destroyed

    def test_modification(self):
        # XXX combacsa 20090805 1905
        # Write an articles
        article_no = self._dummy_article_write(self.session_key_mikkang)
        # Modify its contents
        article_dic = {'title': u'MODIFIED TITLE', 'content': u'MODIFIED CONTENT'}
        result = server.article_manager.modify(self.session_key_mikkang, u'board', article_no, WrittenArticle(**article_dic))
        self.assertEqual(article_no, result)
        # Now check it is modified or not
        expected_result = "[Article(attach=None, board_name=None, author_username=u'mikkang', hit=1, blacklisted=False, title=u'MODIFIED TITLE', deleted=False, read_status=None, root_id=1, is_searchable=True, author_nickname=u'mikkang', content=u'MODIFIED CONTENT', vote=0, depth=1, reply_count=None, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type=None, id=1)]"
        self.assertEqual(expected_result, repr(server.article_manager.read(self.session_key_mikkang, u'board', 1)))
        # XXX : 수정된 글의 경우 ... 
        #       이미 읽은 유저가 읽을 때 조회수가 올라가야 할까?

    def test_read_and_hit_goes_up(self):
        # Write an article
        article_no = self._dummy_article_write(self.session_key_mikkang)
        # Author read the article
        server.article_manager.read(self.session_key_mikkang, u'board', 1)
        # Another person read the article, and check hit goes up.
        result = server.article_manager.read(self.session_key_serialx, u'board', 1)
        expected_result = "[Article(attach=None, board_name=None, author_username=u'mikkang', hit=2, blacklisted=False, title=u'TITLE', deleted=False, read_status=None, root_id=1, is_searchable=True, author_nickname=u'mikkang', content=u'CONTENT', vote=0, depth=1, reply_count=None, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type=None, id=1)]"
        self.assertEqual(expected_result, repr(result))
        # If author read the article again, it should not goes up.
        result = server.article_manager.read(self.session_key_mikkang, u'board', 1)
        self.assertEqual(expected_result, repr(result))
        # XXX : 제 3의 인물이 또 읽으면 hit 이 올라가는 거.

    def test_vote(self):
        # Writel an article
        article_no = self._dummy_article_write(self.session_key_mikkang)
        # Mikkang now vote
        server.article_manager.vote_article(self.session_key_mikkang, u'board', article_no)
        # So the vote status must be updated.
        expected_result = "[Article(attach=None, board_name=None, author_username=u'mikkang', hit=1, blacklisted=False, title=u'TITLE', deleted=False, read_status=None, root_id=1, is_searchable=True, author_nickname=u'mikkang', content=u'CONTENT', vote=1, depth=1, reply_count=None, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type=None, id=1)]"
        self.assertEqual(expected_result, repr(server.article_manager.read(self.session_key_mikkang, u'board', 1)))
        # Serialx now vote
        server.article_manager.vote_article(self.session_key_serialx, u'board', article_no)
        # So the vote status must be updated again.
        expected_result = "[Article(attach=None, board_name=None, author_username=u'mikkang', hit=1, blacklisted=False, title=u'TITLE', deleted=False, read_status=None, root_id=1, is_searchable=True, author_nickname=u'mikkang', content=u'CONTENT', vote=2, depth=1, reply_count=None, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type=None, id=1)]"
        self.assertEqual(expected_result, repr(server.article_manager.read(self.session_key_mikkang, u'board', 1)))
        # But he can't vote again.
        try:
            server.article_manager.vote_article(self.session_key_serialx, u'board', article_no)
            self.fail()
        except InvalidOperation:
            pass

    def test_todays_best_and_weekly_best(self):
        # XXX : Insufficient. To test properly, we must faking time sharply.
        # Write 5 articles.
        # XXX : 왜 content=None 이어야 하지 ??
        for i in range(1, 6):
            self._dummy_article_write(self.session_key_mikkang, unicode(i))
        result = server.article_manager.get_today_best_list(5)
        repr_data = "[Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE5', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536005.100000001, date=31536005.100000001, author_id=2, type='today', id=5), Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE4', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536004.100000001, date=31536004.100000001, author_id=2, type='today', id=4), Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE3', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536003.100000001, date=31536003.100000001, author_id=2, type='today', id=3), Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE2', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536002.100000001, date=31536002.100000001, author_id=2, type='today', id=2), Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE1', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type='today', id=1)]"
        self.assertEqual(repr_data, repr(result))
        result = server.article_manager.get_weekly_best_list(5)
        repr_data = "[Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE5', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536005.100000001, date=31536005.100000001, author_id=2, type='weekly', id=5), Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE4', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536004.100000001, date=31536004.100000001, author_id=2, type='weekly', id=4), Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE3', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536003.100000001, date=31536003.100000001, author_id=2, type='weekly', id=3), Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE2', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536002.100000001, date=31536002.100000001, author_id=2, type='weekly', id=2), Article(attach=None, board_name=u'board', author_username=u'mikkang', hit=0, blacklisted=False, title=u'TITLE1', deleted=False, read_status=None, root_id=None, is_searchable=True, author_nickname=u'mikkang', content=None, vote=0, depth=None, reply_count=0, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type='weekly', id=1)]"
        self.assertEqual(repr_data, repr(result))

    def test_many_replies(self):
        article_id = self._dummy_article_write(self.session_key_mikkang)
        reply_dic = WrittenArticle(**{'title':u'dummy', 'content': u'asdf'})
        article_reply_id_1 = server.article_manager.write_reply(self.session_key_mikkang, u'board', article_id, reply_dic)
        article_reply_id_2 = server.article_manager.write_reply(self.session_key_mikkang, u'board', article_reply_id_1, reply_dic)
        article_reply_id_3 = server.article_manager.write_reply(self.session_key_mikkang, u'board', article_reply_id_2, reply_dic)
        article_reply_id_4 = server.article_manager.write_reply(self.session_key_mikkang, u'board', article_id, reply_dic)
        # Now check some
        article = server.article_manager.read(self.session_key_mikkang, u'board', article_id)
        self.assertEqual(article_id, article[0].root_id)
        self.assertEqual(article_id, article[1].root_id)
        self.assertEqual(article_id, article[2].root_id)
        self.assertEqual(article_id, article[3].root_id)
        self.assertEqual(article_id, article[4].root_id)
        self.assertEqual(1, article[0].depth)
        self.assertEqual(2, article[1].depth)
        self.assertEqual(3, article[2].depth)
        self.assertEqual(4, article[3].depth)
        self.assertEqual(2, article[4].depth)
        # And check reply_count
        list = server.article_manager.article_list(self.session_key_mikkang, u'board', 1, 5)
        self.assertEqual(4, list.hit[0].reply_count)

    def test_blacklist(self):
        # mikkang write an article. mikkang was in serialx's blacklist.
        # Then mikkang's article should be marked as blacklisted.
        # XXX 아라라 프로젝트 생각 :
        # 장기적으로는 Middleware 가 Frontend 에게 보내는 정보량을
        # 어떻게 최소화할 지에 대해서도 생각해야한다 ... (combacsa)
        server.blacklist_manager.add(self.session_key_serialx, u'mikkang')
        article_id = self._dummy_article_write(self.session_key_mikkang)
        self.assertEqual("[Article(attach=None, board_name=None, author_username=u'mikkang', hit=1, blacklisted=True, title=u'TITLE', deleted=False, read_status=None, root_id=1, is_searchable=True, author_nickname=u'mikkang', content=u'CONTENT', vote=0, depth=1, reply_count=None, last_modified_date=31536001.100000001, date=31536001.100000001, author_id=2, type=None, id=1)]", repr(server.article_manager.read(self.session_key_serialx, u'board', 1)))

    def test_article_list_below(self):
        for i in range(100):
            self._dummy_article_write(self.session_key_mikkang)

        l = server.article_manager.article_list_below(self.session_key_mikkang, u'board', 75, 10)
        self.assertEqual(l.hit[0].id, 80)
        self.assertEqual(l.last_page, 10)
        l = server.article_manager.article_list_below(self.session_key_mikkang, u'board', 84, 10)
        self.assertEqual(l.hit[0].id, 90)
        l = server.article_manager.article_list_below(self.session_key_mikkang, u'board', 95, 10)
        self.assertEqual(l.hit[0].id, 100)

    def test_not_read_article_list(self):
        for i in range(110):
            self._dummy_article_write(self.session_key_mikkang)

        l = server.article_manager.not_read_article_list(self.session_key_mikkang)
        self.assertEqual(l.hit, [110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91])

        _ = server.article_manager.read(self.session_key_mikkang, u'board', 110)
        l = server.article_manager.not_read_article_list(self.session_key_mikkang)
        # XXX: 잘못 구현되어 있습니당. article_manager.py의 주석 참조
        self.assertEqual(l.hit, [109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ArticleManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
