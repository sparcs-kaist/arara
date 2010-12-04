#-*- coding: utf:-8 -*-
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
import arara.util
import etc.arara_settings

import time

class Test(unittest.TestCase):
    def setUp(self):
        # Common preparation for all tests
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = False
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        self.engine = arara_engine.ARAraEngine()

        # Fake time for further test
        def stub_time():
            return 1.1
        self.org_time = time.time
        time.time = stub_time

    def test_smart_unicode(self):
        str = u'ABC123가나다'
        cp949_string = unicode(str).encode('cp949')
        utf_8_string = unicode(str).encode('utf-8')
        self.assertEqual(str, arara.util.smart_unicode(cp949_string))
        self.assertEqual(str, arara.util.smart_unicode(utf_8_string))
        self.assertEqual(str, arara.util.smart_unicode(str))

    def test_intlist_to_string_to_intlist(self):
        a = range(1024, 0, -3)
        b = arara.util.intlist_to_string(a)
        c = arara.util.string_to_intlist(b)
        if a != c:
            self.fail( repr(a) + " / " + repr(c))

    def test_split_list(self):
        a = [1, 2, 3, 4, 5, 6, 7]
        result = arara.util.split_list(a, 4)
        self.assertEqual([[1, 2], [3, 4], [5, 6], [7]], result)

        a = [1, 2]
        result = arara.util.split_list(a, 3)
        self.assertEqual([[1], [2], []], result)

    def tearDown(self):
        self.engine.shutdown()
        arara.model.clear_test_database()
        # Restore the time
        time.time = self.org_time
        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED
def suite():
    return unittest.TestLoader().loadTestsFromTestCase(Test)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
