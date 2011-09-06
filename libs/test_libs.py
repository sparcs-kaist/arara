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

    def test_smart_unicode(self):
        # ABC123가나다, 라는 문자열을 이용하여 검사
        unicode_string = u'ABC123\uac00\ub098\ub2e4'
        cp949_string = 'ABC123\xb0\xa1\xb3\xaa\xb4\xd9'
        utf_8_string = 'ABC123\xea\xb0\x80\xeb\x82\x98\xeb\x8b\xa4'
        self.assertEqual(unicode_string, libs.smart_unicode(cp949_string))
        self.assertEqual(unicode_string, libs.smart_unicode(utf_8_string))
        self.assertEqual(unicode_string, libs.smart_unicode(unicode_string))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(LibsTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
