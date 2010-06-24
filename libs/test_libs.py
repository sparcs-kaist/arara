#-*- coding: utf:-8 -*-
import unittest
import os
import sys

arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(arara_path)

import libs

class LibsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_libs(self):
        result = libs.timestamp2datetime(0.0)
        self.assertEqual('1970-01-01 09:00:00', str(result))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(LibsTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
