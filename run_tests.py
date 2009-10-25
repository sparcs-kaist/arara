#!/usr/bin/python2.5

import sys
import os
import unittest

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './gen-py/'))
sys.path.append(PROJECT_PATH)
sys.path.append(THRIFT_PATH)

import arara.test_set

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(arara.test_set.suite()) 
