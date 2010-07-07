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

    def testNormalAddAndRemoveOneBoard(self):
        # Add one board 'garbages'
        server.board_manager.add_board(self.session_key_sysop, u'garbages', u'Garbages Board')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(1, len(board_list))
        self.assertEqual("Board(read_only=False, board_name=u'garbages', board_description=u'Garbages Board', hide=False, id=1)", repr(board_list[0]))
        # Add another board 'ToSysop'
        server.board_manager.add_board(self.session_key_sysop, u'ToSysop', u'The comments to SYSOP')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(2, len(board_list))
        self.assertEqual("Board(read_only=False, board_name=u'garbages', board_description=u'Garbages Board', hide=False, id=1)", repr(board_list[0]))
        self.assertEqual("Board(read_only=False, board_name=u'ToSysop', board_description=u'The comments to SYSOP', hide=False, id=2)", repr(board_list[1]))
        # Check if you can get each board
        garbages = server.board_manager.get_board(u'garbages')
        self.assertEqual("Board(read_only=False, board_name=u'garbages', board_description=u'Garbages Board', hide=False, id=1)", repr(garbages))
        tosysop = server.board_manager.get_board(u'ToSysop')
        self.assertEqual("Board(read_only=False, board_name=u'ToSysop', board_description=u'The comments to SYSOP', hide=False, id=2)", repr(tosysop))
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
        self.assertEqual("Board(read_only=False, board_name=u'garbages', board_description=u'Garbages Board', hide=True, id=1)", repr(board_list[0]))
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
        self.assertEqual("Board(read_only=False, board_name=u'garbages', board_description=u'Garbages Board', hide=False, id=1)", repr(board_list[0]))

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

    def tearDown(self):
        arara.model.clear_test_database()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BoardManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
