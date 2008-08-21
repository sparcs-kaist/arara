#!/usr/bin/python
import os
import sys
import optparse
import traceback
import xmlrpclib
import logging
import logging.handlers

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(PROJECT_PATH)

import arara
import arara.model

from thirdparty import wsgiserver

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

handler_for_info = logging.handlers.RotatingFileHandler('arara_server.log', 'a', 2**20*50, 10)
handler_for_debug = logging.handlers.RotatingFileHandler('arara_server_debug.log', 'a', 2**20*50, 10)
formatter = logging.Formatter('%(asctime)s [%(process)d:%(thread)X] <%(name)s> ** %(levelname)s ** %(message)s')
handler_for_debug.setFormatter(formatter)
handler_for_info.setFormatter(formatter)
handler_for_debug.setLevel(logging.DEBUG)
handler_for_info.setLevel(logging.INFO)

logging.getLogger('').setLevel(logging.NOTSET)
logging.getLogger('').addHandler(handler_for_debug)
logging.getLogger('').addHandler(handler_for_info)

class DetailedFaultXMLRPCDispatcher(SimpleXMLRPCDispatcher):
    def _marshaled_dispatch(self, data, dispatch_method = None):
        """Dispatches an XML-RPC method from marshalled (XML) data.

        XML-RPC methods are dispatched from the marshalled (XML) data
        using the _dispatch method and the result is returned as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided as an argument (see comment in
        SimpleXMLRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing is the prefered means
        of changing method dispatch behavior.
        """

        try:
            params, method = xmlrpclib.loads(data)

            # generate response
            if dispatch_method is not None:
                response = dispatch_method(method, params)
            else:
                response = self._dispatch(method, params)
            # wrap response in a singleton tuple
            response = (response,)
            response = xmlrpclib.dumps(response, methodresponse=1,
                                       allow_none=self.allow_none, encoding=self.encoding)
        except xmlrpclib.Fault, fault:
            response = xmlrpclib.dumps(fault, allow_none=self.allow_none,
                                       encoding=self.encoding)
        except:
            # report exception back to server
            response = xmlrpclib.dumps(
                xmlrpclib.Fault(1, "%s:%s\n%s" % (sys.exc_type, sys.exc_value, traceback.format_exc())),
                encoding=self.encoding, allow_none=self.allow_none,
                )

        return response

dispatcher = DetailedFaultXMLRPCDispatcher(allow_none=False, encoding=None)
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

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port=", dest="port", default=8000, type="int",
                      help="The port to bind")
    options, args = parser.parse_args()
    print "Opening ARAra XMLRPC middleware on port", options.port, "..."
    
    server = wsgiserver.CherryPyWSGIServer(
                ('0.0.0.0', options.port), arara_app,
                numthreads=20,
                server_name='www.arara')

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

# vim: set et ts=8 sw=4 sts=4
