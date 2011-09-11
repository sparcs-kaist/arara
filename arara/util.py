# -*- coding: utf-8 -*-
import traceback
import logging
import time
import smtplib
from email.MIMEText import MIMEText

from arara import model
from etc import arara_settings
from arara_thrift.ttypes import *


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


def send_mail(subject, mailto, content, subtype='html', charset='euc_kr'):
    '''
    ARA 서버에서 E-Mail을 전송하는 함수

    @type  subject: string
    @param subject: 제목
    @type  mailto: string
    @param mailto: 받는 사람
    @type  content: string
    @param content: 메일 내용
    @type  subtype: string
    @param subtype: Content-Type minor type
    @type  charset: string
    @param charset: Character Set
    '''
    from etc.arara_settings import MAIL_SENDER, MAIL_HOST

    try:
        msg = MIMEText(content, _subtype=subtype, _charset=charset)
        msg['Subject'] = subject
        msg['From'] = MAIL_SENDER
        msg['To'] = mailto

        s = smtplib.SMTP()
        s.connect(MAIL_HOST)
        s.sendmail(MAIL_SENDER, [mailto], msg.as_string())
        s.quit()
    except Exception:
        raise

