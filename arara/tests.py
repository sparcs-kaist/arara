import unittest
import doctest
import sys
import os

PROJECT_PATH = os.path.join(os.path.dirname(__file__), '../')
DOCTEST_PATH = os.path.join(PROJECT_PATH, 'arara/test')
sys.path.append(PROJECT_PATH)

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
                               doctest.DocFileSuite(os.path.join(DOCTEST_PATH,
                                   'article_manager.txt')),
                               doctest.DocFileSuite(os.path.join(DOCTEST_PATH,
                                   'member_manager.txt')),
                               #doctest.DocFileSuite(os.path.join(DOCTEST_PATH,
                               #    'blacklist_manager.txt')),
                               doctest.DocFileSuite(os.path.join(DOCTEST_PATH,
                                   'messaging_manager.txt')),
                               doctest.DocFileSuite(os.path.join(DOCTEST_PATH,
                                   'login_manager.txt')),
                               #doctest.DocFileSuite(os.path.join(DOCTEST_PATH,
                               #    'notice_manager.txt')),
                               #doctest.DocFileSuite(os.path.join(DOCTEST_PATH,
                               #    'read_status_manager.txt')),
                               #doctest.DocTestSuite(blacklist_manager),
                               #doctest.DocTestSuite(logging_manager),
                               #doctest.DocTestSuite(log_manager),
                               #doctest.DocTestSuite(notice_manager),
                               #doctest.DocTestSuite(read_status_manager),
                               #doctest.DocTestSuite(sysop_manager),
                               ]
                              )

if __name__ == "__main__":
    try: 
        import testoob 
        testoob.main(defaultTest="suite") 
    except ImportError: 
        unittest.TextTestRunner().run(suite()) 
        #unittest.TextTestRunner(verbosity=2).run(suite())

# vim: set et ts=8 sw=4 sts=4
