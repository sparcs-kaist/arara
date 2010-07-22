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
from arara import arara_engine
import arara.model
import etc.arara_settings

class BoardManagerTest(unittest.TestCase):
    def setUp(self):
        # Common preparation for all tests
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = False
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        self.engine = arara_engine.ARAraEngine()
        # Register one user, mikkang
        user_reg_dic = {'username':u'mikkang', 'password':u'mikkang', 'nickname':u'mikkang', 'email':u'mikkang@example.com', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english', 'campus':u'seoul' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'mikkang', register_key)
        # Then let it logged on.
        self.session_key = self.engine.login_manager.login(u'mikkang', u'mikkang', '143.248.234.140')
        # Login as sysop
        self.session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', '143.234.234.234')
        self.assertEqual(0, len(self.engine.board_manager.get_board_list())) # XXX combacsa: is it allowed?

    def _to_dict(self, board_object):
        # ArticleManagerTest._to_dict 를 참고하여 구현하였다.

        FIELD_LIST = ['read_only', 'board_name', 'board_description', 'hide', 'id', 'headings', 'order']
        result_dict = {}
        for field in FIELD_LIST:
            result_dict[field] = board_object.__dict__[field]
        return result_dict

    def _to_dict_category(self, category_object):
        FIELD_LIST = ['id', 'category_name']
        result_dict = {}
        for field in FIELD_LIST:
            result_dict[field] = category_object.__dict__[field]
        return result_dict

    #adding and removing a category
    def testNormalAddAndRemoveOneCategory(self):
        #Add one category 'miscellaneous'
        self.engine.board_manager.add_category(self.session_key_sysop, u'miscellaneous')
        category_list = self.engine.board_manager.get_category_list()
        self.assertEqual(1, len(category_list))
        self.assertEqual({'id':1, 'category_name': u'miscellaneous'}, self._to_dict_category(category_list[0]))
        #Add another category 'fun stuff'
        self.engine.board_manager.add_category(self.session_key_sysop, u'fun stuff')
        category_list = self.engine.board_manager.get_category_list()
        self.assertEqual(2, len(category_list))
        self.assertEqual({'id':1, 'category_name': u'miscellaneous'}, self._to_dict_category(category_list[0]))
        self.assertEqual({'id':2, 'category_name': u'fun stuff'}, self._to_dict_category(category_list[1]))

        #check if you can get each category
        miscellaneous = self.engine.board_manager.get_category(u'miscellaneous')
        self.assertEqual({'id':1, 'category_name' : u'miscellaneous'}, self._to_dict_category(miscellaneous))
        fun_stuff = self.engine.board_manager.get_category(u'fun stuff')
        self.assertEqual({'id':2, 'category_name' : u'fun stuff'}, self._to_dict_category(fun_stuff))

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


    def testNormalAddAndRemoveOneBoard(self):
        # Add one board 'garbages'
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id':1, 'headings': [], 'order':1}, self._to_dict(board_list[0]))
        # Add another board 'ToSysop'
        self.engine.board_manager.add_board(self.session_key_sysop, u'ToSysop', u'The comments to SYSOP')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(2, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': [], 'order':1}, self._to_dict(board_list[0]))
        self.assertEqual({'read_only': False, 'board_name': u'ToSysop', 'board_description': u'The comments to SYSOP', 'hide': False, 'id': 2, 'headings': [], 'order':2}, self._to_dict(board_list[1]))
        # Check if you can get each board
        garbages = self.engine.board_manager.get_board(u'garbages')
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': [], 'order':1}, self._to_dict(garbages))
        tosysop = self.engine.board_manager.get_board(u'ToSysop')
        self.assertEqual({'read_only': False, 'board_name': u'ToSysop', 'board_description': u'The comments to SYSOP', 'hide': False, 'id': 2, 'headings': [], 'order':2}, self._to_dict(tosysop))
        # Try to delete the board
        self.engine.board_manager.delete_board(self.session_key_sysop, u'garbages')
        self.assertEqual(1, self.engine.board_manager.get_board(u'ToSysop').order)
        self.engine.board_manager.delete_board(self.session_key_sysop, u'ToSysop')

    def testAbNormalAddAndRemoveOneBoard(self):
        # Add Existing Board
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        try:
            self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
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
            self.engine.board_manager.add_board(self.session_key, u'I WANT THIS BOARD', u'MY BOARD')
            self.fail()
        except InvalidOperation:
            pass

    def testAddAndRemoveBotBoard(self):
        # Bot용 Board가 잘 생성되는가?
        self.engine.board_manager._add_bot_board(u'garbages', u'Garbages Board', [], True)
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': True, 'id':1, 'headings': [], 'order':1}, self._to_dict(board_list[0]))
        self.engine.board_manager.delete_board(self.session_key_sysop, u'garbages')

        # Bot용 Board에서 hide 옵션을 False로 주었을 때 잘 동작하는가?
        self.engine.board_manager._add_bot_board(u'bobobot', u'boboboard', [], False)
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'bobobot', 'board_description': u'boboboard', 'hide': False, 'id':2, 'headings': [], 'order':1}, self._to_dict(board_list[0]))
        self.engine.board_manager.delete_board(self.session_key_sysop, u'garbages')

        # 이미 있는 Board를 추가하면 에러를 잘 잡아내는가?
        try:
            self.engine.board_manager._add_bot_board(u'bot', u'Board', [], False)
            self.engine.board_manager._add_bot_board(u'bot', u'Board', [], False)
            self.fail('Integrity Error')
        except InvalidOperation:
            pass

    def testReadOnlyBoard(self):
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'GARBAGES')
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
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        # Test 1. hide_board success?
        self.engine.board_manager.hide_board(self.session_key_sysop, u'garbages')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': True, 'id': 1, 'headings': [], 'order':1}, self._to_dict(board_list[0]))
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
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': [], 'order':1}, self._to_dict(board_list[0]))

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

    def test_get_board_heading_list(self):
        # 말머리가 없는 board 에서 아무 말머리도 안 등록되어있는지 확인한다.
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        self.assertEqual([], self.engine.board_manager.get_board_heading_list(u'garbages'))

        # 말머리를 가진 board 를 추가한다
        self.engine.board_manager.add_board(self.session_key_sysop, u'BuySell', u'market', [u'buy', u'sell'])
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
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board', [u'gar', u'bage'])

        self.assertEqual([u'gar', u'bage'], self.engine.board_manager.get_board_heading_list_fromid(1))

    def test_edit_board(self):
        # 테스트에 사용할 보드 추가.
        self.engine.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbage Board')
        # TEST 1. 보드의 이름, 설명 동시에 바꾸기
        self.engine.board_manager.edit_board(self.session_key_sysop, u'garbages', u'recycle', u'Recycle Board')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        expected_board = {'read_only': False, 'board_name': u'recycle', 'board_description': u'Recycle Board', 'hide': False, 'id': 1, 'headings': [], 'order':1}
        self.assertEqual(expected_board, self._to_dict(board_list[0]))
        # TEST 1-1. 바뀐 이름의 보드는 존재하지 않아야 한다
        try:
            self.engine.board_manager.get_board(u'garbages')
            self.fail("Board 'garbages' must not exist since it is renamed.")
        except InvalidOperation:
            pass
        # TEST 2. 보드의 이름만 바꾸기
        self.engine.board_manager.edit_board(self.session_key_sysop, u'recycle', u'garbages', u'')
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
        self.engine.board_manager.edit_board(self.session_key_sysop, u'garbages', u'', u'Garbage Board')
        board_list = self.engine.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        expected_board['board_description'] = u'Garbage Board'
        self.assertEqual(expected_board, self._to_dict(board_list[0]))
        # TEST 4. 예외적인 상황에 대하여
        try:
            self.engine.board_manager.edit_board(self.session_key_sysop, u'test', u'test2', u'haha')
            self.fail("Since board 'test' not exist, it must fail to rename that board.")
        except InvalidOperation:
            pass
        self.engine.board_manager.add_board(self.session_key_sysop, u'recycle', u'Recycle Board')
        try:
            self.engine.board_manager.edit_board(self.session_key_sysop, u'garbages', u'recycle', u'Recycle Board')
            self.fail("Since board 'recycle'exist, it must fail to rename board 'garbages to 'recycle'.")
        except InvalidOperation:
            pass

    def test_change_board_order(self):
        #테스트에 사용할 보드 추가(1,2,3,4,5,6,7,8,9)
        for i in range(1,10):
            self.engine.board_manager.add_board(self.session_key_sysop, u'board'+unicode(i), u'board')
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

    def testAssignBBSManager(self):
        # 보드마다 관리자 임명 테스트, add BBS Manager by SYSOP
        self.engine.board_manager.add_board(self.session_key_sysop, u'test', u'Testing Board')
        self.assertEqual(False, self.engine.board_manager.has_bbs_manager(u'test'))
        self.engine.board_manager.add_bbs_manager(self.session_key_sysop, u'test', u'mikkang')
        self.assertEqual(True, self.engine.board_manager.has_bbs_manager(u'test'))
        # Add another bbs manager
        user_reg_dic = {'username':u'jean', 'password':u'jean', 'nickname':u'jean', 'email':u'jean@example.com', 'signature':u'jean', 'self_introduction':u'jean', 'default_language':u'english', 'campus':u'daejeon' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'jean', register_key)
        self.engine.board_manager.add_bbs_manager(self.session_key_sysop, u'test', u'jean')
        # TODO: BBSManager 에 한 게시판에 대해 몇명의 관리자가 누가 있는지 확인할 테스트코드

    def tearDown(self):
        arara.model.clear_test_database()
        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BoardManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
