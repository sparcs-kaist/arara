#-*- coding: utf:-8 -*-
import os
import sys
import unittest

ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ARARA_PATH)

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

    def test_intlist_to_string(self):
        self.assertEqual('\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00',
                libs.intlist_to_string([1, 2, 3]))

    def test_string_to_intlist(self):
        self.assertEqual([1, 2, 3],
                libs.string_to_intlist('\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00'))

    def test_filter_dict(self):
        self.assertEqual({'user_id': 1},
                libs.filter_dict({'user_id': 1, 'dummy': 'garbage'}, ['user_id']))

    def test_is_keys_in_dict(self):
        self.assertEqual(True,
                libs.is_keys_in_dict({'user_id': 1, 'dummy': 'garbages'}, ['user_id']))
        self.assertEqual(False,
                libs.is_keys_in_dict({'user_id': 1, 'dummy': 'garbages'}, ['username']))

    def test_intlist_to_string_to_intlist(self):
        a = range(1024, 0, -3)
        b = libs.intlist_to_string(a)
        c = libs.string_to_intlist(b)
        if a != c:
            self.fail(repr(a) + " / " + repr(c))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(LibsTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
