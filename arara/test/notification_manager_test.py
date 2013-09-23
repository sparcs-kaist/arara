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
from etc import arara_settings


class NotiManagerTest(AraraTestBase):
    def setUp(self):
        # Mock Redis
        import redis
        from arara.test.mockup_redis import RedisMockup
        redis.StrictRedis = RedisMockup

        # Common preparation for all tests
        super(NotiManagerTest, self).setUp(stub_time=True, stub_time_initial=1.1)

        # Login as SYSOP and create 'garbage'
        session_key_sysop = self.engine.login_manager.login(
                u'SYSOP', u'SYSOP', u'123.123.123.123')
        self.engine.board_manager.add_board(
                unicode(session_key_sysop), u'garbages', u'쓰레기가 모이는 곳', u'Garbage Board')

        # Register three user, mikkang, hodduc, panda.
        self.session_key_mikkang = self.register_and_login(u'mikkang')
        self.session_key_hodduc = self.register_and_login(u'hodduc')
        self.session_key_panda = self.register_and_login(u'panda')

    def _write_article(self):
        article = Article(**{'title': u'serialx is...', 'content': u'polarbear', 'heading': u''})
        self.engine.article_manager.write_article(
                self.session_key_mikkang, u'garbages', article)

        article = Article(**{'title': u'serialx is...', 'content': u'polarbear', 'heading': u''})
        self.engine.article_manager.write_article(
                self.session_key_mikkang, u'garbages', article)

    def test_empty_noti(self):
        notis = self.engine.noti_manager.get_noti(self.session_key_hodduc)
        self.assertEqual(len(notis), 0)

    def test_reply_and_subscribe(self):
        # 어떤 글을 쓴다
        article = WrittenArticle(**{'title': u'Article', 'content': u'', 'heading': u''})
        aid = int(self.engine.article_manager.write_article(self.session_key_mikkang, u'garbages', article))

        # 특정 thread를 subscribe한다
        self.engine.noti_manager.subscribe(self.session_key_hodduc, aid)
        self.assertTrue(self.engine.noti_manager.is_subscribing(self.session_key_hodduc, aid))

        # 댓글이 달리면 noti가 도착해야 한다
        rid1 = int(self.engine.article_manager.write_reply(self.session_key_panda, u'garbages', aid, article))
        rid2 = int(self.engine.article_manager.write_reply(self.session_key_mikkang, u'garbages', rid1, article))

        notis = self.engine.noti_manager.get_noti(self.session_key_hodduc)
        self.assertEqual(len(notis), 2)
        self.assertTrue(notis[0].type == 1 and notis[1].type == 1)
        self.assertEqual(notis[0].read, False)
        self.assertEqual(notis[0].board_name, 'garbages')
        self.assertTrue(notis[0].article_id == rid2 and notis[1].article_id == rid1)
        self.assertEqual(notis[0].root_title, 'Article')
        self.assertEqual(notis[0].reply_author, 'mikkang')
        self.assertEqual(notis[1].reply_author, 'panda')
        self.assertEqual(notis[0].time, 1.1)

        time.time.elapse(5.0)
        # 다시 불러오면 이제 read 상태여야 한다.
        notis = self.engine.noti_manager.get_noti(self.session_key_hodduc)
        self.assertEqual(len(notis), 2)
        self.assertTrue(notis[0].read and notis[1].read)

        time.time.elapse(5.0)
        # 새로 단 댓글이 내 댓글이면 noti는 도착하지 않아야 한다
        rid3 = int(self.engine.article_manager.write_reply(self.session_key_hodduc, u'garbages', rid1, article))
        notis = self.engine.noti_manager.get_noti(self.session_key_hodduc)
        self.assertEqual(len(notis), 2)
        self.assertTrue(notis[0].read and notis[1].read)

        time.time.elapse(5.0)
        # 내 댓글에 달린 댓글에 대해서는 reply noti만 도착해야 한다
        rid4 = int(self.engine.article_manager.write_reply(self.session_key_panda, u'garbages', rid3, article))
        notis = self.engine.noti_manager.get_noti(self.session_key_hodduc)
        self.assertEqual(len(notis), 3)
        self.assertTrue(not notis[0].read and notis[1].read and notis[2].read)
        self.assertEqual(notis[0].type, 0)
        self.assertEqual(notis[0].time, 16.1)

        # Unsubscribe 한 후에는 도착하지 않아야 한다
        self.engine.noti_manager.unsubscribe(self.session_key_hodduc, aid)
        self.assertFalse(self.engine.noti_manager.is_subscribing(self.session_key_hodduc, aid))
        rid4 = int(self.engine.article_manager.write_reply(self.session_key_panda, u'garbages', rid1, article))
        self.assertEqual(len(notis), 3)

        # Pass

    def test_slice(self):
        # 어떤 글을 쓴다
        article = WrittenArticle(**{'title': u'Article', 'content': u'', 'heading': u''})
        aid = int(self.engine.article_manager.write_article(self.session_key_mikkang, u'garbages', article))

        # 특정 thread를 subscribe한다
        self.engine.noti_manager.subscribe(self.session_key_hodduc, aid)

        # 댓글이 달리면 noti가 도착해야 한다
        rid1 = int(self.engine.article_manager.write_reply(self.session_key_panda, u'garbages', aid, article))
        rid2 = int(self.engine.article_manager.write_reply(self.session_key_mikkang, u'garbages', rid1, article))
        rid3 = int(self.engine.article_manager.write_reply(self.session_key_mikkang, u'garbages', rid1, article))
        rid4 = int(self.engine.article_manager.write_reply(self.session_key_mikkang, u'garbages', rid1, article))
        rid5 = int(self.engine.article_manager.write_reply(self.session_key_mikkang, u'garbages', rid1, article))

        # 4번째 noti부터 2개를 읽어본다.
        notis = self.engine.noti_manager.get_noti(self.session_key_hodduc, offset=3, length=2)
        self.assertEqual(len(notis), 2)
        self.assertEqual(notis[0].article_id, rid2)
        self.assertEqual(notis[1].article_id, rid1)

        # 다시 전부를 읽어본다.
        notis = self.engine.noti_manager.get_noti(self.session_key_hodduc)
        self.assertEqual(len(notis), 5)

    def test_reply_reply(self):
        # 어떤 글을 쓴다
        article = WrittenArticle(**{'title': u'Article', 'content': u'', 'heading': u''})
        aid = int(self.engine.article_manager.write_article(self.session_key_mikkang, u'garbages', article))

        # Panda가 답글을 달았다. Mikkang에게 Noti가 도착했을 것이다.
        rid1 = int(self.engine.article_manager.write_reply(self.session_key_panda, u'garbages', aid, article))
        self.assertEqual(len(self.engine.noti_manager.get_noti(self.session_key_mikkang)), 1)

        # Mikkang이 다시 답글을 달았다. Panda에게 Noti가 도착했을 것이다.
        rid2 = int(self.engine.article_manager.write_reply(self.session_key_mikkang, u'garbages', rid1, article))
        self.assertEqual(len(self.engine.noti_manager.get_noti(self.session_key_panda)), 1)

        # Panda가 다시 답글을.. (생략)
        rid3 = int(self.engine.article_manager.write_reply(self.session_key_panda, u'garbages', rid2, article))
        self.assertEqual(len(self.engine.noti_manager.get_noti(self.session_key_mikkang)), 2)

    #def test_noti_expired(self):  TODO
    #    # 모든 noti는 30일만 유지되어야 한다.
    #    pass

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NotiManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
