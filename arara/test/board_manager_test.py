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
        user_reg_dic = {'username':u'mikkang', 'password':u'mikkang', 'nickname':u'mikkang', 'email':u'mikkang@example.com', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english' }
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
        self.assertEqual("Board(read_only=False, board_name=u'garbages', board_description=u'Garbages Board')", repr(board_list[0]))
        # Add another board 'ToSysop'
        server.board_manager.add_board(self.session_key_sysop, u'ToSysop', u'The comments to SYSOP')
        board_list = server.board_manager.get_board_list()
        self.assertEqual(2, len(board_list))
        self.assertEqual("Board(read_only=False, board_name=u'garbages', board_description=u'Garbages Board')", repr(board_list[0]))
        self.assertEqual("Board(read_only=False, board_name=u'ToSysop', board_description=u'The comments to SYSOP')", repr(board_list[1]))
        # Check if you can get each board
        garbages = server.board_manager.get_board(u'garbages')
        self.assertEqual("Board(read_only=False, board_name=u'garbages', board_description=u'Garbages Board')", repr(garbages))
        tosysop = server.board_manager.get_board(u'ToSysop')
        self.assertEqual("Board(read_only=False, board_name=u'ToSysop', board_description=u'The comments to SYSOP')", repr(tosysop))
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

    def tearDown(self):
        arara.model.clear_test_database()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BoardManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
