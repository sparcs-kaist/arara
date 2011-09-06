#-*- coding: utf-8 -*-
'''
Python Interpreter 의 메모리 사용량에 대한 쏠쏠한 정보를 제공한다.
'''
import gc
import os
import sys

import psutil


def get_physical_memory_allocated():
    '''
    현재 프로세스가 점유하고 있는 메모리의 총량을 구한다.

    @rtype: int
    @return: 현재 프로세스가 점유중인 메모리의 총량 (Byte)

    >>> get_physical_memory_allocated()
    5189632
    '''
    gc.collect()
    return psutil.Process(os.getpid()).get_memory_info().rss


def get_object_memory_allocated():
    '''
    현재 파이썬 인터프리터에 생성되어 있는 객체들의 메모리 점유 총량을 구한다.

    @rtype: int
    @return: 현재 파이썬 인터프리터에 존재하는 객체의 점유 메모리 총량 (Byte)

    >>> get_object_memory_allocated()
    762856
    '''
    gc.collect()
    return reduce(lambda x, y: x + y,
            (sys.getsizeof(item) for item in gc.get_objects()))


def print_memory_allocated():
    '''
    현재의 메모리의 상황을 print 문으로 출력한다.

    >>> print_memory_allocated()
    PHY:       5120 KB, OBJ:        748 KB (      7363 objects)
    '''
    phymem = get_physical_memory_allocated()
    objmem = get_object_memory_allocated()
    print "PHY: %10d KB, OBJ: %10d KB (%10d objects)" % (
            phymem / 1024, objmem / 1024, len(gc.get_objects()))
