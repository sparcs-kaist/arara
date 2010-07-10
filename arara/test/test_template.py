#-*- coding: utf:-8 -*-
# Test template for ARARA Engine.
# 클래스 이름을 적당히 고치고, suite() 함수에 반영하고 사용한다.
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
from arara import arara_engine
import arara.model

import time


class Test(unittest.TestCase):
    def setUp(self):
        # Common preparation for all tests
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        self.engine = arara_engine.ARAraEngine()

        # Fake time for further test
        def stub_time():
            return 1.1
        self.org_time = time.time
        time.time = stub_time

    def tearDown(self):
        arara.model.clear_test_database()
        # Restore the time
        time.time = self.org_time

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(Test)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
