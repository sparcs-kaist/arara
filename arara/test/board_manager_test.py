#-*- coding: utf-8 -*-
import unittest
import os
import sys

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gen-py/'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(ARARA_PATH)

from arara.test.test_common import AraraTestBase
from arara_thrift.ttypes import *
import arara.model
from arara.model import BOARD_TYPE_PICTURE


class BoardManagerTest(AraraTestBase):
    def setUp(self):
        # Common preparation for all tests
        super(BoardManagerTest, self).setUp()

        # Register one user, mikkang
        user_reg_dic = {'username':u'mikkang', 'password':u'mikkang', 'nickname':u'mikkang', 'email':u'mikkang@kaist.ac.kr', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english', 'campus':u'seoul' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'mikkang', register_key)
        # Then let it logged on.
        self.session_key = self.engine.login_manager.login(u'mikkang', u'mikkang', '143.248.234.140')
        # Login as sysop
        self.session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', '143.234.234.234')
        self.assertEqual(0, len(self.engine.board_manager.get_board_list())) # XXX combacsa: is it allowed?

    def _dummy_article_write(self, session_key, title_append = u"", board_name=u'board', heading=u''):
        article_dic = {'title': u'TITLE' + title_append, 'content': u'CONTENT', 'heading': heading}
        return self.engine.article_manager.write_article(session_key, board_name, Article(**article_dic))

    def _to_dict(self, board_object):
        # ArticleManagerTest._to_dict 를 참고하여 구현하였다.

        FIELD_LIST = ['read_only', 'board_name', 'board_description', 'hide', 'id', 'headings', 'order', 'type']
        result_dict = {}
        for field in FIELD_LIST:
            result_dict[field] = board_object.__dict__[field]
        return result_dict

    def _to_dict_category(self, category_object):
        FIELD_LIST = ['id', 'category_name', 'order']
        result_dict = {}
        for field in FIELD_LIST:
            result_dict[field] = category_object.__dict__[field]
        return result_dict

    #adding and removing a category
    def testNormalAddAndRemoveOneCategory(self):
        #Add one category 'miscellaneous'
        self.engine.board_manager.add_category(self.session_key_sysop, 'miscellaneous')
        category_list = self.engine.board_manager.get_category_list()
        self.assertEqual(1, len(category_list))
        self.assertEqual({'id':1, 'category_name': u'miscellaneous', 'order': 1}, self._to_dict_category(category_list[0]))
        #Add another category 'fun stuff'
        self.engine.board_manager.add_category(self.session_key_sysop, 'fun stuff')
        category_list = self.engine.board_manager.get_category_list()
        self.assertEqual(2, len(category_list))
        self.assertEqual({'id':1, 'category_name': u'miscellaneous', 'order': 1}, self._to_dict_category(category_list[0]))
        self.assertEqual({'id':2, 'category_name': u'fun stuff', 'order': 2}, self._to_dict_category(category_list[1]))

        #check if you can get each category
        miscellaneous = self.engine.board_manager.get_category(u'miscellaneous')
        self.assertEqual({'id':1, 'category_name' : u'miscellaneous', 'order': 1}, self._to_dict_category(miscellaneous))
        fun_stuff = self.engine.board_manager.get_category(u'fun stuff')
        self.assertEqual({'id':2, 'category_name' : u'fun stuff', 'order': 2}, self._to_dict_category(fun_stuff))

        #try to delete the category
        self.engine.board_manager.delete_category(self.session_key_sysop, u'miscellaneous')
        self.engine.board_manager.delete_category(self.session_key_sysop, u'fun stuff')

    def testAbNormalAddandRemoveOneCategory(self):
        #Add Existing Category
        self.engine.board_manager.add_category(self.session_key_sysop, u'miscellaneous')
        try:
            self.engine.board_manager.add_category(self.session_key_sysop, u'miscellaneous')
            self.fail()
        except InvalidOperation:
            pass
        #Remove a Category that never existed
        try:
            self.engine.board_manager.delete_category(self.session_key_sysop, u'notice')
            self.fail()
        except InvalidOperation:
            pass

        #access a nonexisting category
        try:
            self.engine.board_manager.get_category(u'notice')
            self.fail()
        except InvalidOperation:
            pass
        #delete category with normal user session
        try:
            self.engine.board_manager.delete_category(self.session_key, u'miscellaneous')
            self.fail()
        except InvalidOperation:
            pass
        self.engine.board_manager.delete_category(self.session_key_sysop, u'miscellaneous')
        #access a deleted category
        try:
            self.engine.board_manager.get_category(u'miscellaneous')
            self.fail()
        except InvalidOperation:
            pass

        #delete a deleted category
        try:
            self.engine.board_manager.delete_category(self.session_key_sysop, u'miscellaneous')
            self.fail()
        except InvalidOperation:
            pass
        #try to add a new category with a normal user session
        try:
            self.engine.board_manager.add_category(self.session_key, u'normal user')
            self.fail()
        except InvalidOperation:
            pass

    def test_edit_category(self):
        # 테스트에 사용할 category 를 하나 만든다.
        self.engine.board_manager.add_category(self.session_key_sysop, u'public')

        # TEST 1. category 이름을 바꾼다.
        self.engine.board_manager.edit_category(self.session_key_sysop, u'public', u'private')
        #         그러면 새 이름으로 카테고리를 찾을 수 있고, 기존 이름으로 찾을 수 없다. 
        result = self.engine.board_manager.get_category(u'private')
        expect = {'id': 1, 'category_name': u'private', u'order': 1}
        self.assertEqual(expect, self._to_dict_category(result))
        try:
            self.engine.board_manager.get_category(u'public')
            self.fail("nonexisting category was returned.")
        except InvalidOperation:
            pass

        # TODO
        # TEST 2. category 이름을 "이미 존재하는 다른 카테고리와 중복되도록" 바꾼다.
        # TEST 3. 존재하지 않는 이름의 category 를 바꾸기를 시도한다.

    def testNormalAddAndRemoveOneBoard(self):
        # Add one board 'garbages'
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'Garbages Board')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id':1, 'headings': [], 'order':1, 'type':0}, self._to_dict(board_list[0]))
        # Add another board 'ToSysop'
        self.engine.board_manager.add_board(self.session_key_sysop, u'ToSysop', u'시삽에게', u'The comments to SYSOP')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(2, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': [], 'order':1, 'type':0}, self._to_dict(board_list[0]))
        self.assertEqual({'read_only': False, 'board_name': u'ToSysop', 'board_description': u'The comments to SYSOP', 'hide': False, 'id': 2, 'headings': [], 'order':2, 'type':0}, self._to_dict(board_list[1]))

        # Check if you can get each board
        garbages = self.engine.board_manager.get_board(u'garbages')
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': [], 'order':1, 'type':0}, self._to_dict(garbages))
        tosysop = self.engine.board_manager.get_board(u'ToSysop')
        self.assertEqual({'read_only': False, 'board_name': u'ToSysop', 'board_description': u'The comments to SYSOP', 'hide': False, 'id': 2, 'headings': [], 'order':2, 'type':0}, self._to_dict(tosysop))

        # Try to delete the board
        self.engine.board_manager.delete_board(self.session_key_sysop, u'garbages')
        self.assertEqual(1, self.engine.board_manager.get_board(u'ToSysop').order)
        self.engine.board_manager.delete_board(self.session_key_sysop, u'ToSysop')

    def testAbNormalAddAndRemoveOneBoard(self):
        # Add Existing Board
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'Garbages Board')
        try:
            self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'Garbages Board')
            fail()
        except InvalidOperation:
            pass
        # Remove never existed board
        try:
            self.engine.board_manager.delete_board(self.session_key_sysop, u'chaos')
            fail()
        except InvalidOperation:
            pass
        # To access to a notexisting board
        try:
            self.engine.board_manager.get_board(u'chaos')
            fail()
        except InvalidOperation:
            pass
        # Try to delete the other remaining board with normal user session
        try:
            self.engine.board_manager.delete_board(self.session_key, u'garbages')
            fail()
        except InvalidOperation:
            pass
        self.engine.board_manager.delete_board(self.session_key_sysop, u'garbages')
        # To access a deleted board
        try:
            self.engine.board_manager.get_board(u'garbages')
            fail()
        except InvalidOperation:
            pass
        # To delete a deleted board
        try:
            self.engine.board_manager.delete_board(self.session_key_sysop, u'garbages')
            # XXX combacsa: This does not pass! Why?
            #self.fail()
        except InvalidOperation:
            pass
        # Try to add new board with normal user session
        try:
            self.engine.board_manager.add_board(self.session_key, u'I WANT THIS BOARD', u'내보드', u'MY BOARD')
            self.fail()
        except InvalidOperation:
            pass

    def testRemoveBoardWithCategories(self):
        # Category 2개를 만들고, 각 카테고리별로 2개의 게시판을 둔다
        self.engine.board_manager.add_category(self.session_key_sysop, u'category1')
        self.engine.board_manager.add_category(self.session_key_sysop, u'category2')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board11', u'board11', u'test', [], u'category1')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board12', u'board12', u'test', [], u'category1')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board21', u'board21', u'test', [], u'category2')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board22', u'board22', u'test', [], u'category2')
        # Category 가 없는 게시판도 2개 만들어 둔다
        self.engine.board_manager.add_board(self.session_key_sysop, u'board1', u'board1', u'test', [])
        self.engine.board_manager.add_board(self.session_key_sysop, u'board2', u'board2', u'test', [])

        # 현 시점에서 게시판의 순서는 [11, 12, 21, 22, 1, 2] 이다.

        # Test 1. board11 을 삭제한다. (가장 위의 게시판) 5개가 바른 순서로 남는지 확인한다.
        self.engine.board_manager.delete_board(self.session_key_sysop, u'board11')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(5, len(board_list))
        self.assertEqual(u'board12', board_list[0].board_name)
        self.assertEqual(u'board21', board_list[1].board_name)
        self.assertEqual(u'board22', board_list[2].board_name)
        self.assertEqual(u'board1',  board_list[3].board_name)
        self.assertEqual(u'board2',  board_list[4].board_name)
        self.assertEqual(1, board_list[0].order)
        self.assertEqual(2, board_list[1].order)
        self.assertEqual(3, board_list[2].order)
        self.assertEqual(4, board_list[3].order)
        self.assertEqual(5, board_list[4].order)

        # Test 2. board2 를 삭제한다. (가장 마지막 게시판) 나머지의 순서에 변동이 없어야 한다.
        self.engine.board_manager.delete_board(self.session_key_sysop, u'board2')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(4, len(board_list))
        self.assertEqual(u'board12', board_list[0].board_name)
        self.assertEqual(u'board21', board_list[1].board_name)
        self.assertEqual(u'board22', board_list[2].board_name)
        self.assertEqual(u'board1',  board_list[3].board_name)
        self.assertEqual(1, board_list[0].order)
        self.assertEqual(2, board_list[1].order)
        self.assertEqual(3, board_list[2].order)
        self.assertEqual(4, board_list[3].order)

        # Test 3. board21 을 삭제한다. (정가운데) board22, board1 만 당겨져야 한다.
        self.engine.board_manager.delete_board(self.session_key_sysop, u'board21')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(3, len(board_list))
        self.assertEqual(u'board12', board_list[0].board_name)
        self.assertEqual(u'board22', board_list[1].board_name)
        self.assertEqual(u'board1',  board_list[2].board_name)
        self.assertEqual(1, board_list[0].order)
        self.assertEqual(2, board_list[1].order)
        self.assertEqual(3, board_list[2].order)

    def testAddAndRemoveBotBoard(self):
        # Bot용 Board가 잘 생성되는가?
        self.engine.board_manager._add_bot_board(u'garbages', u'Garbages Board', [], True)
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': True, 'id':1, 'headings': [], 'order':1, 'type':0}, self._to_dict(board_list[0]))
        self.engine.board_manager.delete_board(self.session_key_sysop, u'garbages')

        # Bot용 Board에서 hide 옵션을 False로 주었을 때 잘 동작하는가?
        self.engine.board_manager._add_bot_board(u'bobobot', u'boboboard', [], False)
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'bobobot', 'board_description': u'boboboard', 'hide': False, 'id':2, 'headings': [], 'order':1, 'type':0}, self._to_dict(board_list[0]))
        self.engine.board_manager.delete_board(self.session_key_sysop, u'garbages')

        # 이미 있는 Board를 추가하면 에러를 잘 잡아내는가?
        try:
            self.engine.board_manager._add_bot_board(u'bot', u'Board', [], False)
            self.engine.board_manager._add_bot_board(u'bot', u'Board', [], False)
            self.fail('Integrity Error')
        except InvalidOperation:
            pass

    def testReadOnlyBoard(self):
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'GARBAGES')
        self.engine.board_manager.add_read_only_board(self.session_key_sysop, u'garbages')
        try:
            self.engine.board_manager.add_read_only_board(self.session_key, u'garbages')
            self.fail()
        except InvalidOperation:
            pass
        try:
            self.engine.board_manager.add_read_only_board(self.session_key_sysop, u'garbages')
            self.fail()
        except InvalidOperation:
            pass
        try:
            self.engine.board_manager.return_read_only_board(self.session_key_sysop, u'chaos')
            self.fail()
        except InvalidOperation:
            pass
        self.engine.board_manager.return_read_only_board(self.session_key_sysop, u'garbages')

    def testHideAndReturnHideBoard(self):
        # Adding new board
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'Garbages Board')
        # Test 1. hide_board success?
        self.engine.board_manager.hide_board(self.session_key_sysop, u'garbages')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': True, 'id': 1, 'headings': [], 'order':1, 'type':0}, self._to_dict(board_list[0]))
        # Test 2. can hide already hidden board?
        try:
            self.engine.board_manager.hide_board(self.session_key_sysop, u'garbages')
            self.fail("Must not hide already hidden board!")
        except InvalidOperation:
            pass

        # Test 3. return_hide_board success?
        self.engine.board_manager.return_hide_board(self.session_key_sysop, u'garbages')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': [], 'order':1, 'type':0}, self._to_dict(board_list[0]))

        # Test 4. can return_hide not hidden board?
        try:
            self.engine.board_manager.return_hide_board(self.session_key_sysop, u'garbages')
            self.fail("Must not return_hide not yet hidden board!")
        except InvalidOperation:
            pass

        # Test 5. Anyone except sysop can do operate?
        # 5-1. hide_board
        try:
            self.engine.board_manager.hide_board(self.session_key, u'garbages')
            self.fail("Someone who is not sysop was able to hide board.")
        except InvalidOperation:
            pass
        # 5-2. return_hide_board
        self.engine.board_manager.hide_board(self.session_key_sysop, 'garbages')
        try:
            self.engine.board_manager.return_hide_board(self.session_key, 'garbages')
            self.fail("Someone who is not sysop was able to show board.")
        except InvalidOperation:
            pass

    def test_add_board_heading(self):
        # 말머리를 가진 board 를 추가한다
        self.engine.board_manager.add_board(self.session_key_sysop, u'BuySell', u'중고장터', u'market', [u'buy'])
        # 새로운 말머리를 추가한다. 
        self.engine.board_manager.add_board_heading(self.session_key_sysop, u'BuySell', u'sell')
        # 잘 추가되었나 검사한다. 
        self.assertEqual([u'buy', u'sell'], self.engine.board_manager.get_board_heading_list(u'BuySell'))
        
        # 이미 있는 말머리를 또 추가하려고 하면 실패해야 한다. 
        try:
            self.engine.board_manager.add_board_heading(self.session_key_sysop, u'BuySell', u'buy')
            self.fail('Must not be able to add an heading already exists')
        except InvalidOperation:
            pass

        # 존재하지 않는 게시판에 말머리를 추가할 수는 없다. 
        try:
            self.engine.board_manager.add_board_heading(self.session_key_sysop, u'Garbages', u'trash')
            self.fail('Must not be able to add an heading to a not-exiting board')
        except InvalidOperation:
            pass

    def test_delete_board_heading(self):
        # 말머리를 가진 board 를 추가한다
        self.engine.board_manager.add_board(self.session_key_sysop, u'BuySell', u'중고장터', u'market', [u'buy', u'sell', u'qna'])
        # 글을 작성한다. 
        self._dummy_article_write(self.session_key, title_append = '1', board_name = 'BuySell', heading = 'buy')
        self._dummy_article_write(self.session_key_sysop, title_append = '2', board_name = 'BuySell', heading = 'buy')
        self._dummy_article_write(self.session_key, title_append = '3', board_name = 'BuySell', heading = 'sell')
        self._dummy_article_write(self.session_key_sysop, title_append = '4', board_name = 'BuySell', heading = 'sell')

        # 말머리를 삭제한다. 
        self.engine.board_manager.delete_board_heading(self.session_key_sysop, 'BuySell', 'buy')
        # 잘 삭제되었나 검사한다. 
        self.assertEqual(['sell', 'qna'], self.engine.board_manager.get_board_heading_list('BuySell'))
        # 게시물이 잘 이동되었나 검사한다.
        self.assertEqual('TITLE2', self.engine.article_manager.article_list(self.session_key_sysop, 'BuySell', '', include_all_headings = False).hit[0].title)
        self.assertEqual('TITLE1', self.engine.article_manager.article_list(self.session_key_sysop, 'BuySell', '', include_all_headings = False).hit[1].title)

        # 이번엔 sell을 삭제하며 qna로 게시물이 옮겨지는지 확인한다. 
        self.engine.board_manager.delete_board_heading(self.session_key_sysop, 'BuySell', 'sell', 'qna')
        # 잘 삭제되었나 검사한다. 
        self.assertEqual(['qna'], self.engine.board_manager.get_board_heading_list('BuySell'))
        # 게시물이 잘 이동되었나 검사한다.
        self.assertEqual('TITLE4', self.engine.article_manager.article_list(self.session_key_sysop, 'BuySell', 'qna', include_all_headings = False).hit[0].title)
        self.assertEqual('TITLE3', self.engine.article_manager.article_list(self.session_key_sysop, 'BuySell', 'qna', include_all_headings = False).hit[1].title)

    def testBoardType(self):
        # 게시판 형식 테스트.
        self.engine.board_manager.add_board(self.session_key_sysop, u'Gallery', u'사진첩', u'All pictures', [], None, BOARD_TYPE_PICTURE)
        gallery = self.engine.board_manager.get_board(u'Gallery')
        self.assertEqual({'read_only': False, 'hide': False, 'board_description': u'All pictures', 'order': 1, 'board_name': u'Gallery', 'headings': [], 'type': 1, 'id': 1}, self._to_dict(gallery))
        self.assertEqual(1, self.engine.board_manager.get_board_type(u'Gallery'))

    def test_get_board_heading_list(self):
        # 말머리가 없는 board 에서 아무 말머리도 안 등록되어있는지 확인한다.
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'Garbages Board')
        self.assertEqual([], self.engine.board_manager.get_board_heading_list(u'garbages'))

        # 말머리를 가진 board 를 추가한다
        self.engine.board_manager.add_board(self.session_key_sysop, u'BuySell', u'중고장터', u'market', [u'buy', u'sell'])
        # 추가된 말머리들이 잘 읽히는지 확인한다
        self.assertEqual([u'buy', u'sell'], self.engine.board_manager.get_board_heading_list(u'BuySell'))

        # 존재하지 않는 게시판의 말머리는 읽어올 수 없어야 한다.
        try:
            self.engine.board_manager.get_board_heading_list(u'noboard')
            self.fail('Must not be able to get board heading list from nonexist board')
        except InvalidOperation:
            pass

    def test_get_board_heading_list_fromid(self):
        # 말머리가 있는 보드를 추가하자
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'Garbages Board', [u'gar', u'bage'])

        self.assertEqual([u'gar', u'bage'], self.engine.board_manager.get_board_heading_list_fromid(1))

    def test_edit_board(self):
        # 테스트에 사용할 보드 추가.
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'쓰레기가 모이는 곳', u'Garbage Board')
        # TEST 1. 보드의 이름, 설명 동시에 바꾸기
        self.engine.board_manager.edit_board(self.session_key_sysop, u'garbages', u'recycle', u'쓰레기가 모였던 곳', u'Recycle Board')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        expected_board = {'read_only': False, 'board_name': u'recycle', 'board_description': u'Recycle Board', 'hide': False, 'id': 1, 'headings': [], 'order':1, 'type':0}
        self.assertEqual(expected_board, self._to_dict(board_list[0]))
        # TEST 1-1. 바뀐 이름의 보드는 존재하지 않아야 한다
        try:
            self.engine.board_manager.get_board(u'garbages')
            self.fail("Board 'garbages' must not exist since it is renamed.")
        except InvalidOperation:
            pass
        # TEST 2. 보드의 이름만 바꾸기
        self.engine.board_manager.edit_board(self.session_key_sysop, u'recycle', u'garbages', u'테스트 alias', u'')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        expected_board['board_name'] = u'garbages'
        self.assertEqual(expected_board, self._to_dict(board_list[0]))
        # TEST 2-1. 바뀐 이름의 보드는 존재하지 않아야 한다
        try:
            self.engine.board_manager.get_board(u'recycle')
            self.fail("Board 'recycle' must not exist since it is renamed.")
        except InvalidOperation:
            pass
        # TEST 3. 보드의 설명만 바꾸기
        self.engine.board_manager.edit_board(self.session_key_sysop, u'garbages', u'', u'', u'Garbage Board')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        expected_board['board_description'] = u'Garbage Board'
        self.assertEqual(expected_board, self._to_dict(board_list[0]))
        # TEST 4. 예외적인 상황에 대하여
        try:
            self.engine.board_manager.edit_board(self.session_key_sysop, u'test', u'test2', u'', u'haha')
            self.fail("Since board 'test' not exist, it must fail to rename that board.")
        except InvalidOperation:
            pass
        self.engine.board_manager.add_board(self.session_key_sysop, u'recycle', u'쓰레기통', u'Recycle Board')
        try:
            self.engine.board_manager.edit_board(self.session_key_sysop, u'garbages', u'recycle', u'', u'Recycle Board')
            self.fail("Since board 'recycle'exist, it must fail to rename board 'garbages to 'recycle'.")
        except InvalidOperation:
            pass
        # TEST 5. 카테고리 변경
        self.engine.board_manager.add_category(self.session_key_sysop, u'cat')
        self.engine.board_manager.edit_board(self.session_key_sysop, u'garbages', u'', u'', u'', u'cat')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, self.engine.board_manager.get_board_list()[0].category_id)

    def test_change_board_category(self):
        self.engine.board_manager.add_category(self.session_key_sysop, u'cate')
        self.engine.board_manager.add_category(self.session_key_sysop, u'gory')
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbage Board', u'cate')
        self.engine.board_manager.change_board_category(self.session_key_sysop, u'garbages', u'gory')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(2, self.engine.board_manager.get_board_list()[0].category_id)

    def test_change_board_order(self):
        #테스트에 사용할 보드 추가(1,2,3,4,5,6,7,8,9)
        for i in range(1,10):
            self.engine.board_manager.add_board(self.session_key_sysop, u'board'+unicode(i), unicode(i), u'board')
        # 뒤에 있는 보드를 앞으로 옮기기 테스트 : board9를 첫 번째로 옮깁니다.(9,1,2,3,4,5,6,7,8)
        self.engine.board_manager.change_board_order(self.session_key_sysop, u'board9', 1)
        self.assertEqual(1, self.engine.board_manager.get_board(u'board9').order)
        self.assertEqual(2, self.engine.board_manager.get_board(u'board1').order)
        self.assertEqual(9, self.engine.board_manager.get_board(u'board8').order)
        # 앞에 있는 보드를 뒤로 옮기기 테스트: board2를 여섯 번째로 옮깁니다.(9,1,3,4,5,2,6,7,8)
        self.engine.board_manager.change_board_order(self.session_key_sysop, u'board2', 6)
        self.assertEqual(6, self.engine.board_manager.get_board(u'board2').order)
        self.assertEqual(5, self.engine.board_manager.get_board(u'board5').order)
        self.assertEqual(3, self.engine.board_manager.get_board(u'board3').order)
        # 캐시된 보드 리스트를 얻었을 때 order에 의해 정렬되어 있는지 검사합니다. 
        expected_result = [u'board'+unicode(i) for i in [9,1,3,4,5,2,6,7,8]]
        actual_result = [board.board_name for board in self.engine.board_manager.get_board_list()]
        self.assertEqual(expected_result, actual_result)
        # 잘못된 order(범위 초과)로 바꾸기를 시도합니다.
        try:
            self.engine.board_manager.change_board_order(self.session_key_sysop, u'board1', 10)
            self.fail("An invalid order provided. The change function must fail.")
        except:
            pass
        # 없는 board의 순서를 바꾸기를 시도합니다.
        try:
            self.engine.board_manager.change_board_order(self.session_key_sysop, u'boardnotexist', 1)
            self.fail("An invalid board provided. The change function must fail.")
        except:
            pass
        # 순서를 지정할 수 없는 bot이 만든 board의 순서 바꾸기를 시도합니다.
        try:
            self.engine.board_manager._add_bot_board(u'botboard', u'bot board', [], True)
            self.engine.board_manager.change_board_order(self.session_key_sysop, u'botboard', 1)
            self.fail("Tried to change the order of 'not-ordered' board. The change function must fail.")
        except:
            pass

    def testChangeAuth(self):
        # 게시판의 읽기/쓰기 권한설정 바꾸기를 테스트, by SYSOP
        self.engine.board_manager.add_board(self.session_key_sysop, u'test', u'테스트보드', u'Testing Board')
        # 읽기/쓰기 권한의 기본값은 3 포탈인증
        self.assertEqual(3, self.engine.board_manager.get_board(u'test').to_read_level)
        self.assertEqual(3, self.engine.board_manager.get_board(u'test').to_write_level)
        # 보드의 권한 값을 바꾸어 봄
        self.engine.board_manager.change_auth(self.session_key_sysop, u'test', 1, 2)
        self.assertEqual(1, self.engine.board_manager.get_board(u'test').to_read_level)
        self.assertEqual(2, self.engine.board_manager.get_board(u'test').to_write_level)

    def testAssignBBSManager(self):
        # 보드마다 관리자 임명 테스트, add BBS Manager by SYSOP
        self.engine.board_manager.add_board(self.session_key_sysop, u'test', u'테스트보드', u'Testing Board')
        self.assertEqual(False, self.engine.board_manager.has_bbs_manager(u'test'))
        self.engine.board_manager.add_bbs_manager(self.session_key_sysop, u'test', u'mikkang')
        self.assertEqual(True, self.engine.board_manager.has_bbs_manager(u'test'))
        # Add another bbs manager
        user_reg_dic = {'username':u'jean', 'password':u'jean', 'nickname':u'jean', 'email':u'jean@kaist.ac.kr', 'signature':u'jean', 'self_introduction':u'jean', 'default_language':u'english', 'campus':u'daejeon' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'jean', register_key)
        self.engine.board_manager.add_bbs_manager(self.session_key_sysop, u'test', u'jean')
        bbs_managers = self.engine.board_manager.get_bbs_managers(u'test')
        self.assertEqual(u'mikkang', bbs_managers[0].username)
        self.assertEqual(u'jean',bbs_managers[1].username)
        # 중복적인 관리자 임명에 대한 체크
        try:
            self.engine.board_manager.add_bbs_manager(self.session_key_sysop, u'test', u'jean')
            self.fail("User is already a manager for the board.")
        except InvalidOperation:
            pass
        # 시삽을 게시판 관리자로 임명하는 경우에 대한 체크
        try:
            self.engine.board_manager.add_bbs_manager(self.session_key_sysop, u'test', u'SYSOP')
            self.fail("SYSOP doesn't need to be assigned as manager.")
        except InvalidOperation:
            pass
        # 게시판 관리자 권한을 체크하기 (사용자 : mikkang)
        user_is_bbs_manager = self.engine.board_manager.is_bbs_manager_of(self.session_key, u'test')
        self.assertEqual(True, user_is_bbs_manager)
        # 게시판 관리자가 아닌 사용자의 권한 체크
        user_reg_dic = {'username':u'mmmmm', 'password':u'mmmmm', 'nickname':u'mmmmm', 'email':u'mmmmm@kaist.ac.kr', 'signature':u'mmmmm', 'self_introduction':u'mmmmm', 'default_language':u'english', 'campus':u'seoul' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'mmmmm', register_key)
        user_session_key = self.engine.login_manager.login(u'mmmmm', u'mmmmm', '143.248.234.140')
        self.assertEqual(False, self.engine.board_manager.is_bbs_manager_of(user_session_key, u'test'))

    def testRemoveBBSManager(self):
        # 게시판 관리자 권한 지우기 테스트. by SYSOP
        self.engine.board_manager.add_board(self.session_key_sysop, u'test', u'테스트보드', u'Testing Board')
        self.engine.board_manager.add_bbs_manager(self.session_key_sysop, u'test', u'mikkang')
        self.assertEqual(True, self.engine.board_manager.has_bbs_manager(u'test'))
        self.engine.board_manager.remove_bbs_manager(self.session_key_sysop, u'test', u'mikkang')
        self.assertEqual(False, self.engine.board_manager.has_bbs_manager(u'test'))

    def testBoardWithCategory(self):
        # 보드를 추가하는 순간부터 특정 카테고리로 집어넣는다
        self.engine.board_manager.add_category(self.session_key_sysop, u'test_category')
        self.engine.board_manager.add_board(self.session_key_sysop, u'test', u'테스트보드', u'Testing Board', [], u'test_category')
        result = self.engine.board_manager.get_board_list()
        board1 = {'id': 1, 'read_only': False, 'board_name': 'test', 'hide': False, 'headings': [], 'order': 1, 'board_description': u'Testing Board', 'type': 0}
        self.assertEqual(1, len(result))
        self.assertEqual(board1, self._to_dict(result[0]))

        # add_bot_board 로 같은 동작을 테스트.
        self.engine.board_manager._add_bot_board(u'test2', u'Testing Board', [], u'test_category')
        result = self.engine.board_manager.get_board_list()
        board2 = {'id': 2, 'read_only': False, 'board_name': 'test2', 'hide': True, 'headings': [], 'order': 2, 'board_description': u'Testing Board', 'type': 0}
        self.assertEqual(2, len(result))
        self.assertEqual(board2, self._to_dict(result[1]))

        # TODO: category 가 제대로 반영이 되고 있는 건가 ??
        expect_dict = {None: [Board(read_only=False, hide=True, board_description=u'Testing Board', order=2, board_name=u'test2', board_alias=u'test2', headings=None, category_id=None, id=2, type=0, to_read_level=3, to_write_level=3)], u'test_category': [Board(read_only=False, hide=False, board_description=u'Testing Board', order=1, board_name=u'test', board_alias=u'테스트보드', headings=None, category_id=1, id=1, type=0, to_read_level=3, to_write_level=3)]}
        expect_list = [[Board(read_only=False, hide=False, board_description=u'Testing Board', order=1, board_name=u'test', board_alias=u'테스트보드', headings=None, category_id=1, id=1, type=0, to_read_level=3, to_write_level=3)], [Board(read_only=False, hide=True, board_description=u'Testing Board', order=2, board_name=u'test2', board_alias=u'test2', headings=None, category_id=None, id=2, type=0, to_read_level=3, to_write_level=3)]]
        self.assertEqual(expect_dict, self.engine.board_manager.get_category_and_board_dict())
        self.assertEqual(expect_list, self.engine.board_manager.get_category_and_board_list())

    def test_get_last_board_order_until_category(self):
        self.engine.board_manager.add_category(self.session_key_sysop, u'cate1')
        self.engine.board_manager.add_category(self.session_key_sysop, u'cate2')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board1', u'1', '', [], u'cate1')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board2', u'2', '', [], u'cate1')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board3', u'3', '', [], u'cate2')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board4', u'4', '', [], None)
        self.assertEqual(2, self.engine.board_manager._get_last_board_order_until_category(u'cate1'))
        self.assertEqual(3, self.engine.board_manager._get_last_board_order_until_category(u'cate2'))
        self.assertEqual(4, self.engine.board_manager._get_last_board_order_until_category(None))

    def test_change_board_order_with_category(self):
        #카테고리 지정
        #테스트에 사용할 카테고리 추가(1,2,3)
        #테스트에 사용하는 보드들(1,2,3  4,5,6,7   8,9,10,11,12  13,14,15)
        for i in range(1,4):
            self.engine.board_manager.add_category(self.session_key_sysop, u'category'+unicode(i))

        self.engine.board_manager.add_board(self.session_key_sysop, u'board13', u'13', u'test')
        for i in range(1,4):
            self.engine.board_manager.add_board(self.session_key_sysop, u'board'+unicode(i), unicode(i), u'test',[] , u'category1')
        for i in range(4,8):
            self.engine.board_manager.add_board(self.session_key_sysop, u'board'+unicode(i), unicode(i), u'test', [], u'category2')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board14', u'14', u'test')
        for i in range(8,13):
            self.engine.board_manager.add_board(self.session_key_sysop, u'board'+unicode(i), unicode(i), u'test', [], u'category3')
        self.engine.board_manager.add_board(self.session_key_sysop, u'board15', u'15', u'test')

        self.assertEqual(1, self.engine.board_manager.get_category(u'category1').order)
        self.assertEqual(2, self.engine.board_manager.get_category(u'category2').order)
        self.assertEqual(3, self.engine.board_manager.get_category(u'category3').order)
        self.assertEqual(1, self.engine.board_manager.get_board(u'board1').order)
        self.assertEqual(13, self.engine.board_manager.get_board(u'board13').order)
        self.assertEqual(4, self.engine.board_manager.get_board(u'board4').order)
        self.assertEqual(14, self.engine.board_manager.get_board(u'board14').order)
        self.assertEqual(8, self.engine.board_manager.get_board(u'board8').order)

        # 잘못된 order로 board 바꾸기
        try:
            self.engine.board_manager.change_board_order(self.session_key_sysop, u'board1', 10)
            self.fail("An invalid order provided. The change function must fail.")
        except:
            pass

        try:
            self.engine.board_manager.change_board_order(self.session_key_sysop, u'board10', 1)
            self.fail("An invalid order provided. The change function must fail.")
        except:
            pass

        #잘못된 order로 카테고리 바꾸기
        try:
            self.engine.board_manager.change_category_order(self.session_key_sysop, u'category1', 20)
            self.fail("An invalid order provided. The change function must fail.")
        except:
            pass

        #카테고리 순서 바꾸기
        self.engine.board_manager.change_category_order(self.session_key_sysop, u'category3', 2)
        self.assertEqual(1, self.engine.board_manager.get_category(u'category1').order)
        self.assertEqual(3, self.engine.board_manager.get_category(u'category2').order)
        self.assertEqual(2, self.engine.board_manager.get_category(u'category3').order)
        self.assertEqual(1, self.engine.board_manager.get_board(u'board1').order)
        self.assertEqual(2, self.engine.board_manager.get_board(u'board2').order)
        self.assertEqual(3, self.engine.board_manager.get_board(u'board3').order)
        self.assertEqual(4, self.engine.board_manager.get_board(u'board8').order)
        self.assertEqual(5, self.engine.board_manager.get_board(u'board9').order)
        self.assertEqual(6, self.engine.board_manager.get_board(u'board10').order)
        self.assertEqual(7, self.engine.board_manager.get_board(u'board11').order)
        self.assertEqual(8, self.engine.board_manager.get_board(u'board12').order)
        self.assertEqual(9, self.engine.board_manager.get_board(u'board4').order)
        self.assertEqual(10, self.engine.board_manager.get_board(u'board5').order)
        self.assertEqual(11, self.engine.board_manager.get_board(u'board6').order)
        self.assertEqual(12, self.engine.board_manager.get_board(u'board7').order)
        self.assertEqual(13, self.engine.board_manager.get_board(u'board13').order)
        self.assertEqual(14, self.engine.board_manager.get_board(u'board14').order)
        self.assertEqual(15, self.engine.board_manager.get_board(u'board15').order)

        #카테고리 삭제 후의 순서
        #self.engine.board_manager.delete_category(self.session_key_sysop, u'category3')

        #self.assertEqual(4, self.engine.board_manager.get_board(u'board4').order)
        #self.assertEqual(5, self.engine.board_manager.get_board(u'board5').order)
        #self.assertEqual(6, self.engine.board_manager.get_board(u'board6').order)
        #self.assertEqual(7, self.engine.board_manager.get_board(u'board7').order)
        #self.assertEqual(8, self.engine.board_manager.get_board(u'board13').order)
        #self.assertEqual(9, self.engine.board_manager.get_board(u'board14').order)
        #self.assertEqual(10, self.engine.board_manager.get_board(u'board15').order)

    def testAddBotCategory(self):
        # Bot용 Category 생성 점검
        self.engine.board_manager._add_bot_category(u'test')
        self.engine.board_manager._add_bot_board(u'test', 'test', [])
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'test', 'board_description': u'test', 'hide': True, 'id':1, 'headings': [], 'order':1, 'type': 0}, self._to_dict(board_list[0]))
        category_list = self.engine.board_manager.get_category_list()
        self.assertEqual(1, len(category_list))
        self.assertEqual({'order': 1, 'category_name': 'test', 'id': 1}, self._to_dict_category(category_list[0]))

        # 이미 있는 Category를 추가하면 에러를 잘 잡아내는가?
        try:
            self.engine.board_manager._add_bot_category(u'bot')
            self.engine.board_manager._add_bot_category(u'bot')
            self.fail('Integrity Error must occur')
        except InvalidOperation:
            pass

    def tearDown(self):
        # Common tearDown
        super(BoardManagerTest, self).tearDown()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BoardManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
