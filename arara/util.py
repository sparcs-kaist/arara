# -*- coding: utf-8 -*-

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
