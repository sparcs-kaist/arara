# -*- coding: utf-8 -*-

import traceback
import logging

def log_method_call_with_source_important(source):

    def log_method_call(function):
        def wrapper(self, session_key, *args, **kwargs):
            logger = logging.getLogger(source)
            if self.login_manager:
                ret, user_info = self.login_manager.get_session(session_key)
                logger.info("FUNCTION %s.%s%s is called by '%s'", source, function.func_name, repr(args), user_info['username'])
            else:
                logger.info("CALL %s.%s%s", source, function.func_name, repr(args))
            try:
                ret = function(self, session_key, *args, **kwargs)
            except:
                logger.error("EXCEPTION %s.%s%s:\n%s", source, function.func_name,
                        repr(args), traceback.format_exc())
                return False, 'INTERNAL_SERVER_ERROR'
            logger.debug("RETURN %s.%s%s=%s", source, function.func_name, repr(args), repr(ret))
            return ret

        return wrapper

    return log_method_call


def log_method_call_with_source(source):

    def log_method_call(function):
        def wrapper(self, *args, **kwargs):
            logger = logging.getLogger(source)
            logger.debug("CALL %s.%s%s", source, function.func_name, repr(args))
            try:
                ret = function(self, *args, **kwargs)
            except:
                logger.error("EXCEPTION %s.%s%s:\n%s", source, function.func_name,
                        repr(args), traceback.format_exc())
                return False, 'INTERNAL_SERVER_ERROR'
            logger.debug("RETURN %s.%s%s=%s", source, function.func_name, repr(args), repr(ret))
            return ret

        return wrapper

    return log_method_call


def require_login(function):
    """
    로그인이 되어 있을 때에만 작동하는 메소드로 만들어주는 데코레이터.
    """
    def wrapper(self, session_key, *args):
        if not self.login_manager.is_logged_in(session_key):
            return False, 'NOT_LOGGEDIN'
        else:
            return function(self, session_key, *args)
    return wrapper


def filter_dict(dictionary, keys):
    """Dictionary is filtered by the given keys."""
    new_dict = {}
    for key in dictionary:
        if key in keys:
            new_dict[key] = dictionary[key]
    return new_dict


def is_keys_in_dict(dictionary, keys):
    for key in keys:
        if not key in dictionary:
            return False
    return True
