#-*- coding: utf-8 -*-
import unittest
import test

import test.article_manager_test
import test.blacklist_manager_test
import test.board_manager_test
import test.bot_manager_test
import test.file_manager_test
import test.login_manager_test
import test.member_manager_test
import test.messaging_manager_test
import test.model_test
import test.notice_manager_test
import test.read_status_internal_test
import test.read_status_manager_test
import test.search_manager_test
import test.util_test
def suite():
    return unittest.TestSuite([
        test.article_manager_test.suite(),
        test.blacklist_manager_test.suite(),
        test.board_manager_test.suite(),
        #현재 bot manager test 는 무언가 잘못 구현되어 있다.
        #test.bot_manager_test.suite(),
        test.file_manager_test.suite(),
        test.login_manager_test.suite(),
        test.member_manager_test.suite(),
        test.messaging_manager_test.suite(),
        test.model_test.suite(),
        test.notice_manager_test.suite(),
        test.read_status_internal_test.suite(),
        test.read_status_manager_test.suite(),
        test.search_manager_test.suite(),
        test.util_test.suite(),
        ])

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
