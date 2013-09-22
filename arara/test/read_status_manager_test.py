#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import time

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara.read_status.db_backend import ReadStatusManagerDB
from arara.test.test_common import AraraTestBase
from arara_thrift.ttypes import *
import arara.model
from arara import model
from etc import arara_settings


class ReadStatusManagerTest(AraraTestBase):
    store_type = 'maindb'

    # Decorator for skipping the test if store type is redis
    def skip_test_if_redis(function):
        def wrap(self, *args, **kwargs):
            if self.store_type == 'redis':
                print >>sys.stderr, 'skip ... Not needed on redis ... ',
            else:
                function(self, *args, **kwargs)
        return wrap

    # Decorator for skipping the test if store type is maindb
    def skip_test_if_maindb(function):
        def wrap(self, *args, **kwargs):
            if self.store_type == 'maindb':
                print >>sys.stderr, 'skip ... Not needed on maindb ... ',
            else:
                function(self, *args, **kwargs)
        return wrap

    def setUp(self):
        # Common preparation for all tests
        super(ReadStatusManagerTest, self).setUp(stub_time=True, stub_time_initial=1.1, read_status_store_type=self.store_type)

        # Login as SYSOP and create 'garbage'
        session_key_sysop = self.engine.login_manager.login(
                u'SYSOP', u'SYSOP', u'123.123.123.123')
        self.engine.board_manager.add_board(
                unicode(session_key_sysop), u'garbages', u'쓰레기가 모이는 곳', u'Garbage Board')
 
        # Register one user, mikkang
        self.session_key_mikkang = self.register_and_login(u'mikkang')

    def _write_articles(self):
        article = Article(**{'title': u'serialx is...', 'content': u'polarbear', 'heading': u''})
        self.engine.article_manager.write_article(
                self.session_key_mikkang, u'garbages', article)

        article = Article(**{'title': u'serialx is...', 'content': u'polarbear', 'heading': u''})
        self.engine.article_manager.write_article(
                self.session_key_mikkang, u'garbages', article)

    def test_check_stat(self):
        self._write_articles()
        ret = self.engine.read_status_manager.check_stat(
                self.session_key_mikkang, 1)
        self.assertEqual("N", ret)

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
            self.engine.read_status_manager.check_stats('asdfasdf', [1,2])
            self.fail()
        except NotLoggedIn:
            pass

    def test_check_stats_by_id(self):
        ret = self.engine.read_status_manager.check_stats_by_id(2, [1, 2])
        self.assertEqual(["N", "N"], ret)

        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 1)
        ret = self.engine.read_status_manager.check_stats_by_id(2, [1, 2])
        self.assertEqual(["R", "N"], ret)

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
            self.engine.read_status_manager.mark_as_read('asdfasdf', 1)
            self.fail()
        except NotLoggedIn:
            pass

    @skip_test_if_redis
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
            self.engine.read_status_manager.mark_as_viewed('asdfasdf', 1)
            self.fail()
        except NotLoggedIn:
            pass

    @skip_test_if_redis
    def test_save_read_status_to_database(self):
        # mikkang 이 2개의 게시물을 작성
        self._write_articles()

        # SYSOP 이 2번 글을 읽음
        session_key_sysop = self.engine.login_manager.login('SYSOP', 'SYSOP', '127.0.0.1')
        self.engine.article_manager.read_article(session_key_sysop, 'garbages', 2)

        # SYSOP 에 대한 정보를 ReadStatusManager 에서 제거
        self.engine.read_status_manager.save_users_read_status_to_database([1])

        # 실제로 정보가 제거되었는지 확인
        self.assertEqual({}, self.engine.read_status_manager.read_status)

        # 실제로 정보가 저장되었는지 확인
        read_status = model.Session().query(model.ReadStatus).filter_by(id=1).one()
        self.assertEqual('\x03\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00', read_status.read_status_numbers)
        self.assertEqual('NRN', read_status.read_status_markers)

    @skip_test_if_redis
    def test_get_read_status_loaded_users(self):
        # 아무 유저도 글을 읽거나 하지 않은 상태를 점검
        self.assertEqual([], self.engine.read_status_manager.get_read_status_loaded_users())

        # mikkang 이 2개의 게시물을 작성
        self._write_articles()

        # SYSOP 이 2번 글을 읽음
        session_key_sysop = self.engine.login_manager.login('SYSOP', 'SYSOP', '127.0.0.1')
        self.engine.article_manager.read_article(session_key_sysop, 'garbages', 2)

        # 이제 글 읽음 정보가 하나는 존재하여야 함
        self.assertEqual([1], self.engine.read_status_manager.get_read_status_loaded_users())

        # SYSOP 이 사라지면 글 읽음 정보가 하나도 없어야 함
        self.engine.read_status_manager.save_to_database(1)
        self.assertEqual([], self.engine.read_status_manager.get_read_status_loaded_users())

    @skip_test_if_maindb
    def test_unmark_all_articles(self):
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 1)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 2)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 3)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 4)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 5)

        self.engine.read_status_manager.unmark_all_articles(self.session_key_mikkang)

        ret = self.engine.read_status_manager.check_stats(self.session_key_mikkang, [1, 2, 3, 4, 5, 6])
        self.assertEqual(["N", "N", "N", "N", "N", "N"], ret)

    @skip_test_if_maindb
    def test_mark_until_number_as_read(self):
        for i in range(50):
            self._write_articles()

        # 100 개의 글이 이미 존재하던 게시판에서
        self.engine.read_status_manager.mark_all_articles(self.session_key_mikkang)

        self._write_articles()

        # 모든 글을 읽은 것으로 처리하고 101 번 글까지 읽어보면
        ret = self.engine.read_status_manager.check_stats(self.session_key_mikkang, range(1, 102))

        # 결론은 당연히 100 번까지는 읽은 것, 101 번 글부터는 읽지 않은 것으로 떠야 한다.
        self.assertEqual(["R"] * 100 + ["N"], ret)

        # unmark_all_articles 와 연동되어도 문제없이 작동하는 것을 확인해 보자.
        self.engine.read_status_manager.unmark_all_articles(self.session_key_mikkang)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 2)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 5)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 11)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 29)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 81)
        self.engine.read_status_manager.mark_as_read(self.session_key_mikkang, 101)

        ret = self.engine.read_status_manager.check_stats(self.session_key_mikkang, range(1, 102))
        self.assertEqual(["N", "R", "N", "N", "R", "N", "N", "N", "N", "N",
                          "R", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                          "N", "N", "N", "N", "N", "N", "N", "N", "R", "N",
                          "N", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                          "N", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                          "N", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                          "N", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                          "N", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                          "R", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                          "N", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                          "R"], ret)


    def tearDown(self):
        super(ReadStatusManagerTest, self).tearDown()


class ReadStatusManagerTestRedis(ReadStatusManagerTest):
    store_type = 'redis'
    def setUp(self):
        # Mock Redis
        import redis
        from arara.test.mockup_redis import RedisMockup
        redis.StrictRedis = RedisMockup
        # Ok. setup.
        super(ReadStatusManagerTestRedis, self).setUp()

def suite():
    suite_db = unittest.TestLoader().loadTestsFromTestCase(ReadStatusManagerTest)
    suite_redis = unittest.TestLoader().loadTestsFromTestCase(ReadStatusManagerTestRedis)
    return unittest.TestSuite([suite_db, suite_redis])

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
