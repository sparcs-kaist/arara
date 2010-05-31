#!/usr/bin/python
#-*- encoding: utf-8 -*-
# CherryPy 를 사용하여 Warara 서버를 실행한다.
import os
import sys
# XXX(serialx): ugly hack for the unicode
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('./gen-py')
import optparse

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(PROJECT_PATH)

os.environ['DJANGO_SETTINGS_MODULE'] = 'warara.settings'

from django.core.handlers.wsgi import WSGIHandler

import os

from thirdparty import wsgiserver  # cherrypy wsgi server

warara_app = WSGIHandler()

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port=", dest="port", default=8001, type="int",
                      help="The port to bind")
    options, args = parser.parse_args()
    print "Opening ARAra Web Frontend on port", options.port, "..."

    server = wsgiserver.CherryPyWSGIServer(
        ('0.0.0.0', options.port),
        warara_app,
        server_name='www.warara',
        numthreads = 20,
    )
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

# vim: set et ts=8 sw=4 sts=4
