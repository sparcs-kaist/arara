
def require_login(function):
    def wrapper(self, session_key, *args):
        if not self.login_manager.is_logged_in(session_key):
            return False, 'NOT_LOGGEDIN'
        else:
            return function(self, session_key, *args)
    return wrapper
