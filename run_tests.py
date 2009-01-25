#/usr/bin/python2.5

import sys
import os
import unittest

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './gen-py/'))
sys.path.append(PROJECT_PATH)
sys.path.append(THRIFT_PATH)

import arara.tests

if __name__ == '__main__':
    try: 
        import testoob 
        testoob.main(defaultTest="arara.tests.suite") 
    except ImportError: 
        unittest.TextTestRunner().run(arara.tests.suite()) 
