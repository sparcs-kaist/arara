import unittest
import doctest
import sys
sys.path.append('../')

from arara import article_manager
from arara import blacklist_manager
from arara import logging_manager
from arara import login_manager
from arara import log_manager
from arara import member_manager
from arara import messaging_manager
from arara import notice_manager
from arara import read_status_manager
from arara import sysop_manager

def suite():
    return unittest.TestSuite([
                               doctest.DocTestSuite(article_manager),
                               #doctest.DocTestSuite(blacklist_manager),
                               #doctest.DocTestSuite(logging_manager),
                               doctest.DocTestSuite(login_manager),
                               #doctest.DocTestSuite(log_manager),
                               doctest.DocTestSuite(member_manager),
                               #doctest.DocTestSuite(messaging_manager),
                               #doctest.DocTestSuite(notice_manager),
                               #doctest.DocTestSuite(read_status_manager),
                               #doctest.DocTestSuite(sysop_manager),
                               ]
                              )

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
