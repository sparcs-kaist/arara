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


def smart_unicode(string):
    '''
    주어진 문자열이 unicode 라면 그대로 리턴, 그렇지 않다면 unicode 로 만듦.
    해당 문자열이 utf-8 인코딩 또는 cp949 인코딩임을 가정.

    >>> smart_unicode(u'아라')
    u'\uc544\ub77c'
    >>> smart_unicode('아라')
    u'\uc544\ub77c'
    >>> smart_unicode(u'아라'.encode('cp949'))
    u'\uc544\ub77c'

    @type string: unicode / str
    @rtype: unicode
    '''
    if isinstance(string, unicode):
        return string
    else:
        try:
            return unicode(string, 'utf-8')
        except UnicodeDecodeError:
            return unicode(string, 'cp949')
