#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
Thrift 코드로부터 생성된 ARAra Thrift Interface 에 존재하는 메소드의 목록과,
arara/arara_engine.py 에 정의된 ARAra Engine 의 인스턴스의 메소드의 목록 비교.

예를 들어 changeset fd0c93a4a39c 까지 적용된 revision 1831 에서는 이렇게 나온다.

$ tools/test_thrift_engine_mismatches.py

 * ARAraEngine misses several functions defined in Thrift Interface

     _update_monitor_status
     change_listing_mode

 * Thrift Interface misses several functions defined in ARAraEngine

     delete_category
     edit_category
     shutdown

'''
import inspect
import os
import sys

ARARA_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
THRIFT_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gen-py'))
sys.path.append(ARARA_PATH)
sys.path.append(THRIFT_PATH)

from arara_thrift import ARAraThriftInterface
from arara import arara_engine
from arara import model


def main():
    model.init_test_database()
    interface_class = ARAraThriftInterface.Iface
    handler_instance = arara_engine.ARAraEngine()

    interface_method_name_list = [x[0] for x in inspect.getmembers(interface_class, predicate=inspect.ismethod)]
    handler_method_name_list   = [x[0] for x in inspect.getmembers(handler_instance, predicate=inspect.ismethod)]

    engine_miss_api = [x for x in interface_method_name_list
            if not x in handler_method_name_list and not x in ['__init__']]
    api_miss_engine = [x for x in handler_method_name_list
            if not x in interface_method_name_list and not x in ['__init__']]

    if engine_miss_api:
        print " * ARAraEngine misses several functions defined in Thrift Interface"
        print
        for function in engine_miss_api:
            print "    ", function
        print

    if api_miss_engine:
        print " * Thrift Interface misses several functions defined in ARAraEngine"
        print
        for function in api_miss_engine:
            print "    ", function
        print

if __name__ == "__main__":
    main()
