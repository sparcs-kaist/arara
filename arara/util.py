# -*- coding: utf-8 -*-

import traceback
import logging
import datetime
import time
import struct

from arara import model
from etc import arara_settings
from arara_thrift.ttypes import *

import thread


def smart_unicode(string):
    '''
    주어진 문자열이 unicode 라면 그대로 리턴하고, 그렇지 않다면 unicode 로 만듦.

    @type string: unicode / string
    @rtype: unicode
    '''
    if isinstance(string, unicode): return string
    else:
        try:
            return unicode(string, 'utf-8')
        except:
            try:
                return unicode(string, 'cp949')
            except:
                raise

from libs import timestamp2datetime, datetime2timestamp

def log_method_call_with_source_important(source):
    '''
    지정된 source 에 Logging 하는 decorator 를 내놓는다.
    이때 여기서 만들어지는 decorator 는 session_key 를 받아야 한다.

    @type  source: string
    @param source: Manager 의 명칭
    '''

    def log_method_call(function):
        '''
        인위적으로 발생시킨 Exception 이 아닌 Exception 이 발생하면 기록을 남기는 decorator.
        단, 함수는 session_key 를 첫번째 파라메터로 받아야 한다.

        @type  function: function
        @param function: 로그를 남기게 하고 싶은 function
        '''
        def wrapper(self, session_key, *args, **kwargs):
            logger = logging.getLogger(source)
            logger.info("CALL(by %s) %s.%s%s", session_key, source,
                    function.func_name, repr(args))

            # XXX: (pipoket) This line shows the status of the pool, remove this later
            if model.pool:
                if arara_settings.ARARA_POOL_DEBUG_MODE:
                    logger.info(model.pool.status())
            try:
                start_time = time.time()
                ret = function(self, session_key, *args, **kwargs)
                duration = time.time() - start_time
            except InvalidOperation:
                raise
            except InternalError:
                raise
            except NotLoggedIn:
                raise
            except:
                logger.error("EXCEPTION(by %s) %s.%s%s:\n%s", session_key, source,
                        function.func_name, repr(args), traceback.format_exc())
                raise InternalError()
            logger.info("DONE(by %s) %s.%s%s, duration: %f", session_key, source, function.func_name, repr(args), duration)
            logger.debug("RETURN(by %s) %s.%s%s=%s", session_key, source,
                    function.func_name, repr(args), repr(ret))

            return ret

        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        return wrapper

    return log_method_call

def log_method_call_with_source_duration(source):
    '''
    지정된 source 에 Logging 하는 decorator 를 내놓는다.

    @type  source: string
    @param source: Manager 의 명칭
    '''

    def log_method_call(function):
        '''
        인위적으로 발생시킨 Exception 이 아닌 Exception 이 발생하면 기록을 남기는 decorator.

        @type  function: function
        @param function: 로그를 남기게 하고 싶은 function
        '''

        def wrapper(self, *args, **kwargs):
            logger = logging.getLogger(source)
            # XXX: (pipoket) This line shows the status of the pool, remove this later
            if model.pool:
                if arara_settings.ARARA_POOL_DEBUG_MODE:
                    logger.info(model.pool.status())
            start_time = time.time()
            ret = function(self, *args, **kwargs)
            duration = time.time() - start_time

            logger.info("DURATION %s.%s%s: %f", source, function.func_name, repr(args), duration)

            return ret

        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        return wrapper

    return log_method_call

def log_method_call_with_source(source):
    '''
    지정된 source 에 Logging 하는 decorator 를 내놓는다.

    @type  source: string
    @param source: Manager 의 명칭
    '''

    def log_method_call(function):
        '''
        인위적으로 발생시킨 Exception 이 아닌 Exception 이 발생하면 기록을 남기는 decorator.

        @type  function: function
        @param function: 로그를 남기게 하고 싶은 function
        '''

        def wrapper(self, *args, **kwargs):
            logger = logging.getLogger(source)
            logger.debug("CALL %s.%s%s", source, function.func_name, repr(args))
            # XXX: (pipoket) This line shows the status of the pool, remove this later
            if model.pool:
                if arara_settings.ARARA_POOL_DEBUG_MODE:
                    logger.info(model.pool.status())
            try:
                start_time = time.time()
                ret = function(self, *args, **kwargs)
                duration = time.time() - start_time
            except InvalidOperation:
                raise
            except InternalError:
                raise
            except NotLoggedIn:
                raise
            except:
                logger.error("EXCEPTION %s.%s%s:\n%s", source, function.func_name,
                        repr(args), traceback.format_exc())
                raise InternalError()
            logger.debug("RETURN %s.%s%s=%s, duration: %f", source, function.func_name, repr(args), repr(ret), duration)

            return ret

        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        return wrapper

    return log_method_call


def require_login(function):
    """
    로그인이 되어 있을 때에만 작동하는 메소드로 만들어주는 데코레이터.
    """
    def wrapper(self, session_key, *args):
        if not self.engine.login_manager.is_logged_in(session_key):
            raise NotLoggedIn()
        else:
            if self.engine.login_manager._update_monitor_status(session_key, str(function.func_name)):
                return function(self, session_key, *args)
            else:
                raise NotLoggedIn()

    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    return wrapper


def filter_dict(dictionary, keys):
    """Dictionary is filtered by the given keys."""
    return dict((x, y) for (x, y) in dictionary.iteritems() if x in keys)

def is_keys_in_dict(dictionary, keys):
    for key in keys:
        if not key in dictionary:
            return False
    return True

def intlist_to_string(int_list):
    length = len(int_list)
    return "".join((struct.pack("i", length), struct.pack("i" * length, *int_list)))

def string_to_intlist(string_):
    length = struct.unpack("i", string_[:4])[0]
    return list(struct.unpack("i" * length, string_[4:]))

def split_list(list, slices):
    '''
    주어진 list 를 slices 갯수만큼의 리스트로 쪼갠다.
    예 : [1, 2, 3, 4, 5, 6, 7] -> [[1, 2], [3, 4], [5,  6], [7]]

    만일 slices 가 len(list) 보다 크면 나머지는 빈 리스트로 채운다.
    예 : [1, 2, 3] -> [[1], [2], [3], [], [], []]

    @type  list: list
    @param list: 쪼갤 list
    @type  slices: int
    @param slices: list 를 쪼갤 갯수
    @rtype: list<list>
    @return: list 를 slices 갯수만큼 쪼갠 list
    '''
    #TODO: 나중에 좀 더 멋있게 하려면 주어진 list 를 slices 갯수만큼의 generator 로 쪼갤수도 있겠다.
    if len(list) < slices:
        return [[x] for x in list] + ([[]] * (slices - len(list)))
    else:
        per = len(list) / slices
        if len(list) % slices > 0:
            per += 1
        result = [None] * slices
        for idx in xrange(slices - 1):
            result[idx] = list[idx * per : (idx + 1) * per]
        result[-1] = list[(slices - 1) * per:]
        return result

def run_job_in_parallel(function, item_list, threads = 4):
    '''
    주어진 item_list 의 원소를 function 에 하나씩 집어넣는다.
    동시에 threads 갯수만큼의 thread 를 돌린다.
    '''
    #TODO: 동작이 잘 되는지 TEST 코드 작성

    available_list = [True] * threads
    index = 0

    def premade_function(function, idx):
        def funct(item):
            function(item)
            available_list[idx] = True
        return funct

    for item in item_list:
        while available_list[index] == False:
            index = (index + 1) % threads

        available_list[index] = False
        thread.start_new_thread(premade_function(function, index), (item,))

    for idx in xrange(len(available_list)):
        while available_list[idx] == False:
            pass
