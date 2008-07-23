#!/usr/bin/python
from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import sys
import optparse

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(PROJECT_PATH)

import arara
import arara.model

from thirdparty import wsgiserver

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port=", dest="port", default=8000, type="int",
                      help="The port to bind")
    options, args = parser.parse_args()
    print "Opening ARAra XMLRPC middleware on port", options.port, "..."
    dispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None)
    arara.model.init_database()
    namespace = arara.get_namespace()
    dispatcher.register_instance(namespace, allow_dotted_names=True)
    
    def arara_app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type','text/xml')]
        start_response(status, response_headers)

        if environ['REQUEST_METHOD'] == 'POST':
            raw_post_data = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH')))
            result = dispatcher._marshaled_dispatch(raw_post_data)
            return result
    
    server = wsgiserver.CherryPyWSGIServer(
                ('0.0.0.0', options.port), arara_app,
                numthreads=1,
                server_name='www.cherrypy.example')

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

# vim: set et ts=8 sw=4 sts=4
