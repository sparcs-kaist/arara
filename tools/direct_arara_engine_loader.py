#-*- coding: utf-8 -*-
'''
ARAraEngine 객체를 생성하고, 디버깅에 유용한 모듈들을 import 한다.
디버깅 편의를 위해 global namespace 에 arara_engine 이라는 인스턴스를 생성.

USAGE:

    $ python -i direct_arara_engine_loader.py

    >>> s = arara_engine.login_manager.login(u"SYSOP", u"SYSOP", "127.0.0.1")
    >>> print_memory_allocated()

tools/memory_inspector.py 를 사용한다.
tools/sqlalchemy_debugger.py 도 사용한다.
'''
import os
import sys

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gen-py'))
ARARA_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(THRIFT_PATH)
sys.path.append(ARARA_PATH)

from arara import arara_engine
from arara import model

from tools.memory_inspector import print_memory_allocated
from tools.sqlalchemy_debugger import compile_query

model.init_database()
arara_engine = arara_engine.ARAraEngine()
