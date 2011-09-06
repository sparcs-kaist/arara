#-*- coding: utf-8 -*-
import logging


class ARAraManager(object):
    '''
    ARAra Engine 의 모든 Manager 는 이 클래스를 상속받는다.
    모든 Manager 는 __public__ 에 외부로 노출할 메소드 목록을 적는다.
    '''

    __public__ = []

    def __init__(self, engine):
        '''
        Manager에 구현된 Public method 들을 engine 에게 노출시킨다.
        Manager에서 사용할 logger를 logging 모듈을 이용하여 등록한다.

        @type  engine: ARAraEngine
        @param engine: 메소드를 노출시킬 엔진
        '''
        self.engine = engine
        self.logger = logging.getLogger(self.__module__.split('.')[-1])
        for function in self.__public__:
            engine.__setattr__(function.__name__,
                    self.__getattribute__(function.__name__))
