#-*- coding: utf-8 -*-
'''
ARAra Engine Backend 에서 memcached 기반 cache 를 구현한다.
'''
from etc import arara_settings

MEMCACHED_CHECKED = False
MEMCACHED_CLIENT  = None

def _check_memcached_available():
    '''
    memcached 가 사용가능하고 사용해야 하는지 확인한다.
    사용가능하면 Memcached Client 를 생성한다.
    '''
    if arara_settings.USE_MEMCACHED:
        try:
            import memcache
            mc = memcache.Client(arara_settings.MEMCACHED_SERVER_LIST, debug=0)
            # 실제로 memcache daemon 이 존재하는지를 확인한다.
            result = mc.set("test", 1)
            if result == True:
                global MEMCACHED_CLIENT
                global MEMCACHED_PREFIX
                MEMCACHED_CLIENT = mc
        except ImportError:
            # memcache 라이브러리가 없으면 그저 캐시를 하지 않을 뿐.
            pass

    global MEMCACHED_CHECKED
    MEMCACHED_CHECKED = True

def _get_key(function_name, arguments):
    def gen():
        yield arara_settings.MEMCACHED_PREFIX
        yield function_name
        for x in arguments:
            yield unicode(x)

    return u".".join(gen()).encode("utf-8")

def memcached_decorator(function):
    '''
    self 가 붙은 어떤 함수가 memcached 를 사용하도록 만든다.
    모든 파라메터는 바로 unicode 객체로 변환 가능해야 한다.

    @type  function: function
    @param function: memcache 를 사용할 함수 (kwargs 사용불가)
    '''
    def wrapper(self, *args):
        if MEMCACHED_CHECKED == False:
            _check_memcached_available()

        if MEMCACHED_CLIENT:
            key = _get_key(function.__name__, args)
            result = MEMCACHED_CLIENT.get(key)
            if not result:
                result = function(self, *args)
                MEMCACHED_CLIENT.set(key, result)
        else:
            result = function(self, *args)

        return result

    wrapper.__name__ = function.__name__
    wrapper.__doc__  = function.__doc__
    return wrapper

def clear_memcached(function, *args):
    '''
    self 가 붙은 어떤 함수에 대한 memcached 값을 제거한다.
    모든 파라메터는 바로 unicode 객체로 변환 가능해야 한다.

    @type  function: function
    @param function: memcache 를 사용하는 함수 (kwargs 사용불가)
    '''
    if MEMCACHED_CHECKED == False:
        _check_memcached_available()

    if MEMCACHED_CLIENT:
        key = _get_key(function.__name__, args)
        MEMCACHED_CLIENT.delete(key)
