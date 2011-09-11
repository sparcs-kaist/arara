#-*- coding: utf-8 -*-
import datetime
import struct
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


def intlist_to_string(int_list):
    '''
    struct 모듈을 이용하여 int 의 list 를 byte string 으로 변환한다.
    int_list 의 길이는 2 ** 31 - 1 를 초과해서는 안 된다.

    >>> intlist_to_string([1, 2, 3])
    '\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00'

    @type  int_list: list<int>
    @param int_list: byte string 으로 변환하려는 int 의 list
    @rtype: str
    @return: byte string 으로 변환된 int 의 list
    '''
    length = len(int_list)
    return "".join((struct.pack("i", length), struct.pack("i" * length, *int_list)))


def string_to_intlist(string):
    '''
    struct 모듈을 이용하여 byte string 을 int 의 list 로 변환한다.
    intlist_to_string 모듈을 사용하여 변환한 문자열만 list 로 변환 가능하다.

    >>> string_to_intlist('\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00')
    [1, 2, 3]

    @type  string: str
    @param string: int 의 list 로 변환하려는 byte string
    @rtype: list<int>
    @return: 변환된 int 의 list
    '''
    length = struct.unpack("i", string[:4])[0]
    return list(struct.unpack("i" * length, string[4:]))


def filter_dict(dictionary, keys):
    """
    주어진 dictionary 에서 keys 에 없는 key 를 제외시킨 새 dictionary 를 반환.

    >>> filter_dict({'user_id': 1, 'dummy': 'garbage'}, ['user_id'])
    {'user_id': 1}

    @type  dictionary: dict
    @param dictionary: Filter 할 dictionary
    @type  keys: list<str>
    @param keys: dictionary 에서 남기고 싶은 key 의 목록
    @rtype: dict
    @return: 해당 key 들이 제거된 새로운 dictionary
    """
    return dict((x, y) for (x, y) in dictionary.iteritems() if x in keys)


def is_keys_in_dict(dictionary, keys):
    '''
    주어진 dictionary 에 keys 에 주어진 key 가 모두 존재하는지를 점검한다.

    >>> is_keys_in_dict({'user_id': 1, 'dummy': 'garbages'}, ['user_id'])
    True
    >>> is_keys_in_dict({'user_id': 1, 'dummy': 'garbages'}, ['username'])
    False

    @type  dictionary: dict
    @param dictionary: key 목록을 점검할 dictionary
    @type  keys: list<str>
    @param keys: dictionary 에 있어야 하는 key 의 목록
    @rtype: bool
    @return: 모든 key 가 있으면 True, 아니면 False
    '''
    for key in keys:
        if not key in dictionary:
            return False
    return True
