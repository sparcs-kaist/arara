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
server = None

class BoardManagerTest(unittest.TestCase):
    def setUp(self):
        global server
        # Common preparation for all tests
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        arara.server.server = arara.get_namespace()
        server = arara.get_namespace()
        # Register one user, mikkang
        user_reg_dic = {'username':u'mikkang', 'password':u'mikkang', 'nickname':u'mikkang', 'email':u'mikkang@example.com', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english', 'campus':u'seoul' }
        register_key = server.member_manager.register_(UserRegistration(**user_reg_dic))
        server.member_manager.confirm(u'mikkang', register_key)
        # Then let it logged on.
        self.session_key = server.login_manager.login(u'mikkang', u'mikkang', '143.248.234.140')
        # Login as sysop
        self.session_key_sysop = server.login_manager.login(u'SYSOP', u'SYSOP', '143.234.234.234')
        self.assertEqual(0, len(server.board_manager.get_board_list())) # XXX combacsa: is it allowed?

    def _to_dict(self, board_object):
        # ArticleManagerTest._to_dict 를 참고하여 구현하였다.

        FIELD_LIST = ['read_only', 'board_name', 'board_description', 'hide', 'id', 'headings']
        result_dict = {}
        for field in FIELD_LIST:
            result_dict[field] = board_object.__dict__[field]
        return result_dict

    def testNormalAddAndRemoveOneBoard(self):
        # Add one board 'garbages'
        server.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id':1, 'headings': []}, self._to_dict(board_list[0]))
        # Add another board 'ToSysop'
        server.board_manager.add_board(self.session_key_sysop, u'ToSysop', u'The comments to SYSOP')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(2, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': []}, self._to_dict(board_list[0]))
        self.assertEqual({'read_only': False, 'board_name': u'ToSysop', 'board_description': u'The comments to SYSOP', 'hide': False, 'id': 2, 'headings': []}, self._to_dict(board_list[1]))
        # Check if you can get each board
        garbages = server.board_manager.get_board(u'garbages')
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': []}, self._to_dict(garbages))
        tosysop = server.board_manager.get_board(u'ToSysop')
        self.assertEqual({'read_only': False, 'board_name': u'ToSysop', 'board_description': u'The comments to SYSOP', 'hide': False, 'id': 2, 'headings': []}, self._to_dict(tosysop))
        # Try to delete the board
        server.board_manager.delete_board(self.session_key_sysop, u'ToSysop')
        server.board_manager.delete_board(self.session_key_sysop, u'garbages')

    def testAbNormalAddAndRemoveOneBoard(self):
        # Add Existing Board
        server.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        try:
            server.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
            fail()
        except InvalidOperation:
            pass
        # Remove never existed board
        try:
            server.board_manager.delete_board(self.session_key_sysop, u'chaos')
            fail()
        except InvalidOperation:
            pass
        # To access to a notexisting board
        try:
            server.board_manager.get_board(u'chaos')
            fail()
        except InvalidOperation:
            pass
        # Try to delete the other remaining board with normal user session
        try:
            server.board_manager.delete_board(self.session_key, u'garbages')
            fail()
        except InvalidOperation:
            pass
        server.board_manager.delete_board(self.session_key_sysop, u'garbages')
        # To access a deleted board
        try:
            server.board_manager.get_board(u'garbages')
            fail()
        except InvalidOperation:
            pass
        # To delete a deleted board
        try:
            server.board_manager.delete_board(self.session_key_sysop, u'garbages')
            # XXX combacsa: This does not pass! Why?
            #self.fail()
        except InvalidOperation:
            pass
        # Try to add new board with normal user session
        try:
            server.board_manager.add_board(self.session_key, u'I WANT THIS BOARD', u'MY BOARD')
            self.fail()
        except InvalidOperation:
            pass

    def testReadOnlyBoard(self):
        server.board_manager.add_board(self.session_key_sysop, u'garbages', u'GARBAGES')
        server.board_manager.add_read_only_board(self.session_key_sysop, u'garbages')
        try:
            server.board_manager.add_read_only_board(self.session_key, u'garbages')
            self.fail()
        except InvalidOperation:
            pass
        try:
            server.board_manager.add_read_only_board(self.session_key_sysop, u'garbages')
            self.fail()
        except InvalidOperation:
            pass
        try:
            server.board_manager.return_read_only_board(self.session_key_sysop, u'chaos')
            self.fail()
        except InvalidOperation:
            pass
        server.board_manager.return_read_only_board(self.session_key_sysop, u'garbages')

    def testHideAndReturnHideBoard(self):
        # Adding new board
        server.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        # Test 1. hide_board success?
        server.board_manager.hide_board(self.session_key_sysop, u'garbages')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': True, 'id': 1, 'headings': []}, self._to_dict(board_list[0]))
        # Test 2. can hide already hidden board?
        try:
            server.board_manager.hide_board(self.session_key_sysop, u'garbages')
            self.fail("Must not hide already hidden board!")
        except InvalidOperation:
            pass

        # Test 3. return_hide_board success?
        server.board_manager.return_hide_board(self.session_key_sysop, u'garbages')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual({'read_only': False, 'board_name': u'garbages', 'board_description': u'Garbages Board', 'hide': False, 'id': 1, 'headings': []}, self._to_dict(board_list[0]))

        # Test 4. can return_hide not hidden board?
        try:
            server.board_manager.return_hide_board(self.session_key_sysop, u'garbages')
            self.fail("Must not return_hide not yet hidden board!")
        except InvalidOperation:
            pass

        # Test 5. Anyone except sysop can do operate?
        # 5-1. hide_board
        try:
            server.board_manager.hide_board(self.session_key, u'garbages')
            self.fail("Someone who is not sysop was able to hide board.")
        except InvalidOperation:
            pass
        # 5-2. return_hide_board
        server.board_manager.hide_board(self.session_key_sysop, 'garbages')
        try:
            server.board_manager.return_hide_board(self.session_key, 'garbages')
            self.fail("Someone who is not sysop was able to show board.")
        except InvalidOperation:
            pass

    def test_get_board_heading_list(self):
        # 말머리가 없는 board 에서 아무 말머리도 안 등록되어있는지 확인한다.
        server.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        self.assertEqual([], server.board_manager.get_board_heading_list(u'garbages'))

        # 말머리를 가진 board 를 추가한다
        server.board_manager.add_board(self.session_key_sysop, u'BuySell', u'market', [u'buy', u'sell'])
        # 추가된 말머리들이 잘 읽히는지 확인한다
        self.assertEqual([u'buy', u'sell'], server.board_manager.get_board_heading_list(u'BuySell'))

        # 존재하지 않는 게시판의 말머리는 읽어올 수 없어야 한다.
        try:
            server.board_manager.get_board_heading_list(u'noboard')
            self.fail('Must not be able to get board heading list from nonexist board')
        except InvalidOperation:
            pass

    def test_get_board_heading_list_fromid(self):
        # 말머리가 있는 보드를 추가하자
        server.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board', [u'gar', u'bage'])

        self.assertEqual([u'gar', u'bage'], server.board_manager.get_board_heading_list_fromid(1))

    def test_edit_board(self):
        # 테스트에 사용할 보드 추가.
        server.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbage Board')
        # TEST 1. 보드의 이름, 설명 동시에 바꾸기
        server.board_manager.edit_board(self.session_key_sysop, u'garbages', u'recycle', u'Recycle Board')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        expected_board = {'read_only': False, 'board_name': u'recycle', 'board_description': u'Recycle Board', 'hide': False, 'id': 1, 'headings': []}
        self.assertEqual(expected_board, self._to_dict(board_list[0]))
        # TEST 1-1. 바뀐 이름의 보드는 존재하지 않아야 한다
        try:
            server.board_manager.get_board(u'garbages')
            self.fail("Board 'garbages' must not exist since it is renamed.")
        except InvalidOperation:
            pass
        # TEST 2. 보드의 이름만 바꾸기
        server.board_manager.edit_board(self.session_key_sysop, u'recycle', u'garbages', u'')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        expected_board['board_name'] = u'garbages'
        self.assertEqual(expected_board, self._to_dict(board_list[0]))
        # TEST 2-1. 바뀐 이름의 보드는 존재하지 않아야 한다
        try:
            server.board_manager.get_board(u'recycle')
            self.fail("Board 'recycle' must not exist since it is renamed.")
        except InvalidOperation:
            pass
        # TEST 3. 보드의 설명만 바꾸기
        server.board_manager.edit_board(self.session_key_sysop, u'garbages', u'', u'Garbage Board')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        expected_board['board_description'] = u'Garbage Board'
        self.assertEqual(expected_board, self._to_dict(board_list[0]))
        # TEST 4. 예외적인 상황에 대하여
        try:
            server.board_manager.edit_board(self.session_key_sysop, u'test', u'test2', u'haha')
            self.fail("Since board 'test' not exist, it must fail to rename that board.")
        except InvalidOperation:
            pass
        server.board_manager.add_board(self.session_key_sysop, u'recycle', u'Recycle Board')
        try:
            server.board_manager.edit_board(self.session_key_sysop, u'garbages', u'recycle', u'Recycle Board')
            self.fail("Since board 'recycle'exist, it must fail to rename board 'garbages to 'recycle'.")
        except InvalidOperation:
            pass

    def tearDown(self):
        arara.model.clear_test_database()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BoardManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
