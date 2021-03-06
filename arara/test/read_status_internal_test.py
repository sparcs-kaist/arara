#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import random

from collections import defaultdict

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara.read_status import ReadStatus

class ReadStatusInternalTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get(self):
        rs = ReadStatus('N')
        self.assertEqual([(0, 'N')], rs.data)

        self.assertEqual(rs.get(0), "N")
        self.assertEqual(rs.get(1), "N")
        self.assertEqual(rs.get(2), "N") 
        self.assertEqual(rs.get(100), "N")
        
        rs.set(1, 'N')
        self.assertEqual(rs.get(1), "N")
        self.assertEqual(rs.get(2), "N") 
        self.assertEqual(rs.get(100), "N")

        self.assertEqual(rs.get_range(xrange(1, 6)), ["N"] * 5)

    def test_set(self):
        rs = ReadStatus('N')
        self.assertEqual([(0, 'N')], rs.data)

        rs.set(1, 'V')
        self.assertEqual(rs.data,
                [(0, 'N'), (1, 'V'), (2, 'N')])

        rs.set(0, 'X')
        self.assertEqual(rs.data,
                [(0, 'X'), (1, 'V'), (2, 'N')])

        rs.set(2, 'V')
        self.assertEqual(rs.data,
                [(0, 'X'), (1, 'V'), (3, 'N')])

        self.assertEqual(rs.get(1), "V")
        self.assertEqual(rs.get(2), "V") 
        self.assertEqual(rs.get(100), "N")

        self.assertEqual(rs.get_range(xrange(1, 6)), 
                ['V', 'V', 'N', 'N', 'N'])

        rs = ReadStatus('N')
        rs.set(5, 'K')
        rs.set(0, 'X')
        self.assertEqual(rs.get_range(xrange(0, 6)),
                ['X', 'N', 'N', 'N', 'N', 'K'])

    def test_getset(self):
        d = defaultdict(lambda: 'N')
        rs = ReadStatus('N')
        for i in range(10):
            n = random.randint(0, 1000)
            v = chr(random.randint(ord('A'), ord('Z')))
            d[n] = v
            rs.set(n, v)
            self.assert_(len(rs.data) <= 1002)
            self.assert_(d[n] == rs.get(n))

        d = defaultdict(lambda: 'N')
        rs = ReadStatus('N')
        log = []
        for i in range(20000):
            n = random.randint(0, 10)
            v = chr(random.randint(ord('A'), ord('Z')))
            log.append((n, v))
            d[n] = v
            rs.set(n, v)
            self.assert_(len(rs.data) <= 12)
            self.assert_(d[n] == rs.get(n))


        d = defaultdict(lambda: 'N')
        rs = ReadStatus('N')
        for i in range(10000):
            n = abs(int(random.gauss(500, 10)))
            v = chr(random.randint(ord('A'), ord('C')))
            d[n] = v
            rs.set(n, v)
            self.assert_(d[n] == rs.get(n))


        d = defaultdict(lambda: 'N')
        rs = ReadStatus('N')
        for i in range(10000):
            n = abs(int(random.gauss(500000000, 100000000)))
            v = chr(random.randint(ord('A'), ord('C')))
            d[n] = v
            rs.set(n, v)
            self.assert_(d[n] == rs.get(n))
        

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ReadStatusInternalTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
