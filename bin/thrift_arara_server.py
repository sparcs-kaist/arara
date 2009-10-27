#!/usr/bin/python
import os
import sys
# XXX(serialx): ugly hack for the unicode
reload(sys)
sys.setdefaultencoding('utf-8')

import optparse
import traceback
import xmlrpclib
import time
import logging
import logging.handlers

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gen-py"))
sys.path.append(THRIFT_PATH)
sys.path.append(PROJECT_PATH)

from arara_thrift.ttypes import *
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

import arara
import arara.model

from arara import MAPPING, DEPENDENCY, PORT, CLASSES, connect_thrift_server
from thirdparty import wsgiserver

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

handler_for_info = logging.handlers.RotatingFileHandler('arara_server.log', 'a', 2**20*50, 10)
formatter = logging.Formatter('%(asctime)s [%(process)d:%(thread)X] <%(name)s> ** %(levelname)s ** %(message)s')
handler_for_info.setFormatter(formatter)
handler_for_info.setLevel(logging.INFO)

#handler_for_debug = logging.handlers.RotatingFileHandler('arara_server_debug.log', 'a', 2**20*50, 10)
#handler_for_debug.setFormatter(formatter)
#handler_for_debug.setLevel(logging.DEBUG)

logging.getLogger('').setLevel(logging.NOTSET)
logging.getLogger('').addHandler(handler_for_info)
#logging.getLogger('').addHandler(handler_for_debug)

    
def open_thrift_server(processor, handler, port):
    handler_instance = handler()
    processor_ = processor.Processor(handler_instance)
    transport = TSocket.TServerSocket(port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolAcceleratedFactory()
    #if handler.__class__.__name__ in ['ArticleManager']:
    #    server = TServer.TForkingServer(processor_, transport, tfactory, pfactory)
    #else:
    #    server = TServer.TThreadedServer(processor_, transport, tfactory, pfactory)
    server = TServer.TThreadPoolServer(processor_, transport, tfactory, pfactory)
    server.setNumThreads(200)
    return server, handler_instance

def setter_name(class_):
    """AbcdEfg -> _set_abcd_efg"""
    class_name = class_.__name__
    char_list = list(class_name)
    if char_list[0].isupper():
        char_list[0] = char_list[0].lower()
    for i, char in enumerate(char_list):
        if char.isupper():
            char_list[i] = char.lower()
            char_list.insert(i, '_')
    concat = ''.join(char_list)
    return '_set_' + concat

def open_server(server_name, base_port):
    assert server_name in CLASSES
    base_class = CLASSES[server_name]
    thrift_class = dict(MAPPING)[base_class]
    port = base_port + PORT[base_class]
    import thread
    server, instance = open_thrift_server(thrift_class, base_class, port)
    thread.start_new_thread(resolve_dependencies, (base_class, instance, base_port))
    return server

def resolve_dependencies(base_class, instance, base_port):
    dependencies = DEPENDENCY[base_class]
    for dependency_class in dependencies:
        dependency_port = base_port + PORT[dependency_class]
        dependency_thrift_class = dict(MAPPING)[dependency_class]
        print 'Connecting to %s in localhost:%d' % (
                dependency_class.__name__, dependency_port)
        while True:
            try:
                client = connect_thrift_server('localhost',
                        base_port, dependency_class)
                setter = setter_name(dependency_class)
                setter_method = getattr(instance, setter)
                setter_method(client)
                break
            except TTransportException:
                print '%s cannot be connected. Retrying...' % dependency_class.__name__
                time.sleep(1)
                continue
    

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port=", dest="port", default=8000, type="int",
                      help="The port to bind")
    options, args = parser.parse_args()
    print "Opening ARAra Thrift middleware on port starting from", options.port, "..."
    
    arara.model.init_database()

    def exception_handler(type_, value, traceback_):
        import traceback
        error_msg = ''.join(traceback.format_exception(type_, value, traceback_))
        print >> sys.stderr, error_msg
        print >> sys.stdout, error_msg

    sys.excepthook = exception_handler

    print args[0]
    server = open_server(args[0], options.port)

    print 'Starting the server...'
    server.serve()
    print 'done.'
    

# vim: set et ts=8 sw=4 sts=4
