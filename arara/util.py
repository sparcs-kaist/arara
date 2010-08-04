# -*- coding: utf-8 -*-

import traceback
import logging
import datetime
import time
import struct

from arara import model
from etc import arara_settings
from arara_thrift.ttypes import *


def smart_unicode(string):
    '''
    주어진 문자열이 unicode 라면 그대로 리턴하고, 그렇지 않다면 unicode 로 만듦.

    @type string: unicode / string
    @rtype: unicode
    '''
    if isinstance(string, unicode): return string
    else: return unicode(string, 'utf-8')

from libs import timestamp2datetime, datetime2timestamp

def update_monitor_status(function):
    # TODO: 이 함수 뭔가 이상하다. 잘못 구현되어 있는 것 같다.
    def wrapper(self, session_key, *args, **kwargs):
        if 'login_manager' in self.__dict__:
            action = function.func_name
            #ret, msg = self.login_manager._update_monitor_status(session_key, action)

def log_method_call_with_source_important(source):
    '''
    지정된 source 에 Logging 하는 decorator 를 내놓는다.

    @type  source: string
    @param source: Manager 의 명칭
    '''

    def log_method_call(function):
        '''
        인위적으로 발생시킨 Exception 이 아닌 Exception 이 발생하면 기록을 남기게 한다.

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
                ret = function(self, session_key, *args, **kwargs)
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
            logger.debug("RETURN(by %s) %s.%s%s=%s", session_key, source,
                    function.func_name, repr(args), repr(ret))

            return ret

        return wrapper

    return log_method_call


def log_method_call_with_source(source):

    def log_method_call(function):
        def wrapper(self, *args, **kwargs):
            logger = logging.getLogger(source)
            logger.debug("CALL %s.%s%s", source, function.func_name, repr(args))
            # XXX: (pipoket) This line shows the status of the pool, remove this later
            if model.pool:
                if arara_settings.ARARA_POOL_DEBUG_MODE:
                    logger.info(model.pool.status())
            try:
                ret = function(self, *args, **kwargs)
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
            logger.debug("RETURN %s.%s%s=%s", source, function.func_name, repr(args), repr(ret))

            return ret

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
            try:
                assert self.engine.login_manager._update_monitor_status(session_key, str(function.func_name))
                assert self.engine.login_manager.update_session(session_key)
                return function(self, session_key, *args)
            except AssertionError:
                session_logger = logging.getLogger('SESSION UPDATER')
                session_logger.error(traceback.format_exc())
                return function(self, session_key, *args)

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
