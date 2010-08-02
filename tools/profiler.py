#!python
# -*- coding:utf-8 -*-

import os
import sys
import time
import inspect
import random
import string

import cProfile

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../gen-py/'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(ARARA_PATH)

from arara_thrift.ttypes import *
from arara import arara_engine
import arara

class DummyAction(object):
    def __init__(self):
        self.engine = arara_engine.ARAraEngine()

        self.sysop_session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'127.0.0.1')
        self.username_list = []
        self.board_name_list = []
        self.article_number_list = []
        self.session_key_list = []

    def register_account(self):
        while True:
            random_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
            if random_id not in self.username_list:
                break
        user_reg_dic = {'username':random_id, 'password':random_id, 'nickname':random_id, 'email':random_id + '@example.com', 'signature':random_id, 'self_introduction':random_id, 'default_language':u'english', 'campus':u'seoul' }
        confirm_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.username_list.append(random_id)
        self.engine.member_manager.confirm(random_id, confirm_key)
        return random_id

    def login(self, username = None):
        if not username: username = random.choice(self.username_list)
        key = self.engine.login_manager.login(username, username, '127.0.0.1')
        self.session_key_list.append(key)
        return key

    def logout(self, session_key = None):
        if len(self.session_key_list) == 0: return None
        if not session_key: session_key = random.choice(self.session_key_list)
        self.engine.login_manager.logout(session_key)

    def login_all(self):
        for username in self.username_list:
            self.login(username)

    def add_board(self, board_name = None):
        while True:
            random_board_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
            if random_board_name not in self.board_name_list:
                break
        self.board_name_list.append(random_board_name)
        return self.engine.board_manager.add_board(self.sysop_session_key, random_board_name, random_board_name)

    def write_article(self, session_key = None, board_name = None, remember_article_number = False):
        if len(self.board_name_list) == 0: return None
        article_dic = {'title': u'DUMMY TITLE', 'content': 'DUMMY CONTENT', 'heading': ''}
        if not session_key: session_key = random.choice(self.session_key_list)
        if not board_name: board_name = random.choice(self.board_name_list)
        added_article_id = self.engine.article_manager.write_article(session_key, board_name, Article(**article_dic))
        if remember_article_number:
            self.article_number_list.append((board_name, added_article_id))
        return (board_name, added_article_id)

    def write_reply(self, session_key = None, board_name = None, root_number = None):
        reply_dic = WrittenArticle(**{'title':u'DUMMY REPLY', 'content': u'DUMMY REPLY CONTENT', 'heading': u''})
        if not session_key: session_key = random.choice(self.session_key_list)
        if not root_number:
            random_article = random.choice(self.article_number_list)
            board_name = random_article[0]
            root_number = random_article[1]
        self.engine.article_manager.write_reply(session_key, board_name, root_number, reply_dic)

    def article_list(self, board_name = None, page_number = 1):
        if len(self.board_name_list) == 0: return None
        if not board_name: board_name = random.choice(self.board_name_list)
        self.engine.article_manager.article_list(self.sysop_session_key, board_name, '')

    def read_article(self, board_name = None, article_number = None):
        if (not board_name) and (not article_number): board_name, article_number = random.choice(self.article_number_list)
        self.engine.article_manager.read_article(self.sysop_session_key, board_name, article_number)
class Profiler(object):
    def __init__(self):
        pass

    def play_scenario(self):
        arara.model.init_test_database()
        self.dummy = DummyAction()

        self.dummy.register_account()
        self.dummy.login_all()
        self.dummy.add_board()

        cProfile.runctx('self.profile_write_article()', globals(), locals(), filename = 'profile_write_article')
        cProfile.runctx('self.profile_article_list()', globals(), locals(), filename = 'profile_article_list')

        arara.model.clear_test_database()

    def profile_write_article(self):
        for i in range(100):
            self.dummy.write_article()

    def profile_article_list(self):
        for i in range(100):
            self.dummy.article_list()

    def profile_read_article(self):
        for i in range(100):
            self.dummy.read_article()

    def _play_real_scenario(self):
        d = self.dummy
        garbage = d.add_board('garbage')
        user1 = d.login()
        d.article_list(garbage)
        article1 = d.write_article(user1, garbage, True)
        d.read_article(garbage, article1[1])
        d.article_list(garbage)
        
        user2 = d.login()
        d.article_list(garbage)
        d.read_article(garbage, article1[1])
        d.write_reply(user2, article1[0], article1[1])
        d.read_article(garbage, article1[1])
        d.article_list(garbage)

        user3 = d.login()
        d.article_list(garbage)
        d.article_list(garbage, 2)
        d.article_list(garbage, 3)
        d.article_list(garbage, 1)
        d.read_article(garbage, article1[1])

        user4 = d.login()
        d.article_list(garbage)
        d.article_list(garbage, 2)
        d.article_list(garbage)
        d.read_article(garbage, article1[1])
        for i in range(30):
            d.article_list(garbage)
            d.read_article(garbage, article1[1])
            d.write_reply(user1, article1[0], article1[1])
            d.read_article(garbage, article1[1])
            d.article_list(garbage)
            d.article_list(garbage)
            d.read_article(garbage, article1[1])
            d.write_reply(user2, article1[0], article1[1])
            d.read_article(garbage, article1[1])
            d.article_list(garbage)
            d.article_list(garbage)
            d.read_article(garbage, article1[1])
            d.write_reply(user4, article1[0], article1[1])
            d.read_article(garbage, article1[1])
            d.article_list(garbage)

    def play_real_scenario(self):
        arara.model.init_test_database()
        self.dummy = DummyAction()
        
        for i in range(400):
            self.dummy.register_account()
        for i in range(10):
            self.dummy.login()
        for i in range(2):
            self.dummy.add_board()
        for i in range(1000):
            self.dummy.write_article(None, None, True)
        for i in range(1000):
            self.dummy.write_reply()

        cProfile.runctx('self._play_real_scenario()', globals(), locals(), filename = 'profile_real_scenario')

        arara.model.clear_test_database()

profiler = Profiler()
#profiler.play_scenario()
profiler.play_real_scenario()
