#-*- coding: utf-8 -*-
import datetime
import time

def timestamp2datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def datetime2timestamp(datetime_):
    '''
    datetime.datetime 객체를 timestamp 형식으로 바꿈
    @type datetime_: datetime.datetime
    @rtype: double
    '''
    # TODO: 이 함수도 libs 밑으로 옮긴다.
    return (time.mktime(datetime_.timetuple())
            + datetime_.microsecond / 1e6)


