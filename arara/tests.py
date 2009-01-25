import unittest
import doctest
import sys
import os

PROJECT_PATH = os.path.join(os.path.dirname(__file__), '../')
THRIFT_PATH = os.path.join(os.path.dirname(__file__), '../gen-py/')
sys.path.append(PROJECT_PATH)
sys.path.append(THRIFT_PATH)

from arara import article_manager
from arara import blacklist_manager
from arara import login_manager
from arara import member_manager
from arara import messaging_manager
from arara import notice_manager
from arara import read_status_manager

import logging

LOG_FILENAME = '/tmp/arara_test.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)


def suite():
    return unittest.TestSuite([
                               #doctest.DocFileSuite(
                               #    'test/article_manager.txt'),
                               #doctest.DocFileSuite(
                               #    'test/member_manager.txt'),
                               #doctest.DocFileSuite(
                               #    'test/blacklist_manager.txt'),
                               #doctest.DocFileSuite(
                               #    'test/messaging_manager.txt'),
                               doctest.DocFileSuite(
                                   'test/login_manager.txt'),
                               #doctest.DocFileSuite(
                               #    'test/model.txt'),
                               #doctest.DocFileSuite(
                               #    'test/notice_manager.txt'),
                               #doctest.DocFileSuite(
                               #    'test/read_status_manager.txt'),
                               #doctest.DocFileSuite(
                               #    'test/file_manager.txt'),
                               #doctest.DocFileSuite(
                               #    'test/board_manager.txt'),
                               #doctest.DocFileSuite(
                               #    'test/search_manager.txt'),
                               #doctest.DocTestSuite(blacklist_manager),
                               #doctest.DocTestSuite(logging_manager),
                               #doctest.DocTestSuite(log_manager),
                               #doctest.DocTestSuite(notice_manager),
                               #doctest.DocTestSuite(read_status_manager),
                               #doctest.DocTestSuite(sysop_manager),
                               ]
                              )

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s <%(name)s> ** %(levelname)s ** %(message)s',
                        filename='arara_tests.log',
                        filemode='w')

    try: 
        import testoob 
        testoob.main(defaultTest="suite") 
    except ImportError: 
        unittest.TextTestRunner().run(suite()) 

# vim: set et ts=8 sw=4 sts=4
