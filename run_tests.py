#!/usr/bin/python2.5
import sys
import os
import unittest

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './gen-py/'))
sys.path.append(PROJECT_PATH)
sys.path.append(THRIFT_PATH)

import arara.test_set
import libs.test_libs

def suite():
    return unittest.TestSuite([
        arara.test_set.suite(),
        libs.test_libs.suite(),
        ])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite()) 
