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

# Time is needed for testing file_manager
import time

class NoticeManagerTest(unittest.TestCase):
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

        # Login as SYSOP and create 'garbage'
        session_key_sysop = server.login_manager.login(
                u'SYSOP', u'SYSOP', u'123.123.123.123')
        server.board_manager.add_board(
                unicode(session_key_sysop), u'garbages', u'Garbage Board')

    def tearDown(self):
        arara.model.clear_test_database()
        # Restore the time
        time.time = self.org_time

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NoticeManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
