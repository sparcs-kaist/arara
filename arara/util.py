# -*- coding: utf-8 -*-

import traceback
import logging
import datetime
import time

from arara import model
from arara.server import get_server
from arara_thrift.ttypes import *

def smart_unicode(string):
    if isinstance(string, unicode): return string
    else: return unicode(string, 'utf-8')

def datetime2timestamp(datetime_):
    return (time.mktime(datetime_.timetuple())
            + datetime_.microsecond / 1e6)

def timestamp2datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def update_monitor_status(function):
    def wrapper(self, session_key, *args, **kwargs):
        if 'login_manager' in self.__dict__:
            action = function.func_name
            #ret, msg = self.login_manager._update_monitor_status(session_key, action)

def log_method_call_with_source_important(source):

    def log_method_call(function):
        def wrapper(self, session_key, *args, **kwargs):
            logger = logging.getLogger(source)
            username = session_key
            #if 'login_manager' in self.__dict__:
            #    action = source + '.' + function.func_name
            #    ret, msg = self.login_manager._update_monitor_status(session_key, action)
            #    try:
            #        assert ret, msg
            #    except AssertionError:
            #        logger.error("EXCEPTION(by %s) %s.%s%s:\n%s", username, source,
            #                function.func_name, repr(args), traceback.format_exc())
            #        raise InternalError()
            #    user_info = self.login_manager.get_session(session_key)
            #    username = user_info.username
            logger.info("CALL(by %s) %s.%s%s", username, source,
                    function.func_name, repr(args))
            # XXX: (pipoket) This line shows the status of the pool, remove this later
            logger.info(model.pool.status())
            #logger.debug("CURRENT USER STATUS UPDATED: User '%s' calls '%s' function",
            #        username, user_info.current_action)
            try:
                ret = function(self, session_key, *args, **kwargs)
            except InvalidOperation:
                raise
            except InternalError:
                raise
            except NotLoggedIn:
                raise
            except:
                logger.error("EXCEPTION(by %s) %s.%s%s:\n%s", username, source,
                        function.func_name, repr(args), traceback.format_exc())
                raise InternalError()
            logger.debug("RETURN(by %s) %s.%s%s=%s", username, source,
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
        if not get_server().login_manager.is_logged_in(session_key):
            raise NotLoggedIn()
        else:
            try:
                assert get_server().login_manager._update_monitor_status(session_key, str(function.func_name))
                assert get_server().login_manager.update_session(session_key)
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
