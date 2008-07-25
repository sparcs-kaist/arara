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
                                   'read_status_internal.txt')),
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
