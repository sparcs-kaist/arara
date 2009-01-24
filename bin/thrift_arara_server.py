#!/usr/bin/python
import os
import sys
import optparse
import traceback
import xmlrpclib
import logging
import logging.handlers

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gen-py"))
sys.path.append(THRIFT_PATH)
sys.path.append(PROJECT_PATH)

import arara_thrift.LoginManager
from arara_thrift.ttypes import *
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

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


arara.model.init_database()
namespace = arara.get_namespace()
    

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port=", dest="port", default=8000, type="int",
                      help="The port to bind")
    options, args = parser.parse_args()
    print "Opening ARAra Thrift middleware on port starting from", options.port, "..."
    
    servers = []

    def open_server(processor, handler, port):
        processor_ = processor.Processor(handler)
        transport = TSocket.TServerSocket(port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TSimpleServer(processor_, transport, tfactory, pfactory)
        servers.append(server)

    open_server(arara_thrift.LoginManager, namespace.login_manager, options.port)

    print 'Starting the server...'
    servers[0].serve()
    print 'done.'
    

# vim: set et ts=8 sw=4 sts=4
