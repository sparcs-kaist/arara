#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
ARAra Middleware 를 띄우는 스크립트.
'''
import os
import sys
# XXX(serialx): ugly hack for the unicode
reload(sys)
sys.setdefaultencoding('utf-8')

import optparse
import traceback
import logging
import logging.handlers

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gen-py"))
sys.path.append(THRIFT_PATH)
sys.path.append(PROJECT_PATH)

from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

from etc import arara_settings
from arara.arara_engine import ARAraEngine
import arara.model

from arara_thrift import ARAraThriftInterface

# LOG 파일 관련 설정
handler_for_info = logging.handlers.RotatingFileHandler(arara_settings.ARARA_LOG_PATH, 'a', 2**20*50, 10)
formatter = logging.Formatter('%(asctime)s [%(process)d:%(thread)X] <%(name)s> ** %(levelname)s ** %(message)s')
handler_for_info.setFormatter(formatter)
handler_for_info.setLevel(logging.INFO)

logging.getLogger('').setLevel(logging.NOTSET)
logging.getLogger('').addHandler(handler_for_info)

if arara_settings.ARARA_DEBUG_HANDLER_ON:
    handler_for_debug = logging.handlers.RotatingFileHandler(arara_settings.ARARA_DEBUG_LOG_PATH, 'a', 2**20*50, 10)
    handler_for_debug.setFormatter(formatter)
    handler_for_debug.setLevel(logging.DEBUG)

    logging.getLogger('').addHandler(handler_for_debug)

    
def open_thrift_server(processor, handler, port):
    '''
    실제 Thrift Server 를 생성한다.

    @type  processor: module
    @param processor: 자동으로 생성된 Thrift Service Class
    @type  handler: Class
    @param handler: Backend Instance 를 생성할 Class
    '''
    handler_instance = handler()
    processor_ = processor.Processor(handler_instance)
    transport = TSocket.TServerSocket(port)
    tfactory = TTransport.TBufferedTransportFactory()
    #tfactory = TTransport.TFramedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolAcceleratedFactory()

    # 서버를 어떻게 띄울 것인가?
    # 1. TThreadedServer   : Thread per Connection
    # 2. TForkingServer    : Process per Connection
    # 3. TThreadPoolServer : Preloaded Thread with Pool

    server = TServer.TThreadPoolServer(processor_, transport, tfactory, pfactory)
    server.setNumThreads(arara_settings.ARARA_NUM_THREADS)
    return server, handler_instance

def open_server(base_port):
    '''
    @type  base_port: int
    @param base_port: 서버의 포트번호 시작점
    '''
    base_class = ARAraEngine
    thrift_class = ARAraThriftInterface
    port = base_port
    logger.info("Opening ARAra Thrift middleware on port starting from %s...", port)
    server, instance = open_thrift_server(thrift_class, base_class, port)
    return server

if __name__ == '__main__':
    logger = logging.getLogger('main')
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port=", dest="port", default=arara_settings.ARARA_SERVER_BASE_PORT, type="int",
                      help="The port to bind")
    options, args = parser.parse_args()
    
    arara.model.init_database()

    def exception_handler(type_, value, traceback_):
        error_msg = ''.join(traceback.format_exception(type_, value, traceback_))
        print >> sys.stderr, error_msg
        print >> sys.stdout, error_msg

    sys.excepthook = exception_handler

    server = open_server(options.port)

    logger.info('Starting the server...')
    server.serve()
    print 'done.'
    

# vim: set et ts=8 sw=4 sts=4
