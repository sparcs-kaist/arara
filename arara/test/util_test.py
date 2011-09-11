#-*- coding: utf:-8 -*-
import unittest
import os
import sys

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara_thrift.ttypes import *
import arara.util


class UtilTest(unittest.TestCase):
    # TODO: util.py 에 있는 함수들을 테스트할 코드를 구현한다.
    pass


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(UtilTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
