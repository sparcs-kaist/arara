import hashlib

from django.core.cache import cache
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'gen-py'))

from arara_thrift.ttypes import *

def check_logged_in(request):
    r = {}
    if "arara_session_key" in request.session:
        sess = request.session['arara_session_key']

        username = request.session['arara_username']
        checksum = hashlib.sha1(sess+"@"+username).hexdigest()
        if request.COOKIES.get('arara_checksum', '') != checksum:
            from warara import warara_middleware
            server = warara_middleware.get_server()
            User_Info = server.member_manager.get_info(sess)
            server.login_manager.debug__check_session(sess, username, request.META['REMOTE_ADDR'], User_Info)
            request.session.flush()

            sess = ""
            r['logged_in'] = False
            r['username'] = ""
            request.session['django_language']="en"
        else:
            r['arara_session'] = sess
            r['logged_in'] = True
            r['username'] = request.session.get('arara_username', 0);
    else:
        sess = ""
        r['logged_in'] = False
        r['username'] = ""
        request.session['django_language']="en"

    return sess, r

def wrap_error_base(template="error.html"):
    def wrap_error_wrap(f):
        def check_error(request, *args, **argv):
            r = {} #render item
            try:
                return f(request, *args, **argv)
            except NotLoggedIn, e:
                r['error_message'] = "You are not logged in!"
                rendered = render_to_string(template, r)
                if "arara_session_key" in request.session:
                    request.session.clear()
                return HttpResponse(rendered)
            except InvalidOperation, e:
                r['error_message'] = e.why
                rendered = render_to_string(template, r)
                return HttpResponse(rendered)
            except InternalError, e:
                r['error_message'] = "Internal Error"
                rendered = render_to_string(template, r)
                return HttpResponse(rendered)
            except IOError, e:
                # board/views.py:file_download() might throwgh this error
                r['error_message'] = "IO Error (File Not Found)"
                rendered = render_to_string(template, r)
                return HttpResponse(rendered)

        return check_error
    return wrap_error_wrap

wrap_error = wrap_error_base()
wrap_error_mobile = wrap_error_base("mobile/error.html")

def cache_page(expire=60):
    def cache_page_wrap(function):
        def wrapper(request, *args, **kwargs):
            if request.method != 'GET':
                return function(request, *args, **kwargs)

            sess, r = check_logged_in(request)
            key = '%s_%s_%s' % (__file__, function.func_name, repr(args))
            logged_in = r['logged_in']
            if logged_in:
                username = r['username']
                key = '%s_%s' % (key, username)

            response = cache.get(key)
            if response == None:
                response = function(request, *args, **kwargs)
                cache.set(key, response, expire)

            return response

        return wrapper
    return cache_page_wrap

def prevent_cached_by_browser(f):
    def wrapper(request, *args, **kwargs):
        response = f(request, *args, **kwargs)
        response['Cache-Control'] = 'max-age=0, no-cache=True'
        return response
    return wrapper

