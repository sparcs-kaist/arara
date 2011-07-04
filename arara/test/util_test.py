#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import time

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara.test.test_common import AraraTestBase
from arara_thrift.ttypes import *
import arara.model
import arara.util


class UtilTest(AraraTestBase):
    def setUp(self):
        # Common preparation for all tests
        super(UtilTest, self).setUp()

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
        # Common tearDown
        super(UtilTest, self).tearDown()

        # Restore the time
        time.time = self.org_time

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(UtilTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
