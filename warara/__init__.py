from django.core.cache import cache
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from arara_thrift.ttypes import *

def check_logged_in(request):
    r = {}
    if "arara_session_key" in request.session:
        sess = request.session['arara_session_key']
        r['logged_in'] = True
        r['username'] = request.session.get('arara_username', 0);
    else:
        sess = ""
        r['logged_in'] = False
        r['username'] = ""
        request.session['django_language']="en"

    return sess, r

def wrap_error(f):
    def check_error(*args, **argv):
        r = {} #render item
        try:
            return f(*args, **argv)
        except NotLoggedIn, e:
            r['error_message'] = e.why
            rendered = render_to_string("error.html", r)
            return HttpResponse(rendered)
        except InvalidOperation, e:
            r['error_message'] = e.why
            rendered = render_to_string("error.html", r)
            return HttpResponse(rendered)
        except InternalError, e:
            r['error_message'] = "Internal Error"
            rendered = render_to_string("error.html", r)
            return HttpResponse(rendered)

    return check_error

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
