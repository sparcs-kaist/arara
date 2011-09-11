#-*- coding: utf-8 -*-
"""
Thrift Server 를 생성한다.
"""
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport


def open_thrift_server(processor, handler, port, server_type, num_threads=None):
    '''
    실제 Thrift Server 를 생성한다.

    @type  processor: Class (Thrift Interface)
    @param processor: 자동으로 생성된 Thrift Service Class
    @type  handler: Class
    @param handler: Thrift Interface 에 연결되어 실제 수행될 함수들이 있는 Class
    @type  port: int
    @param port: Thrift server 를 bind 할 포트
    @type  server_type: str
    @param server_type: in ["TThreadedServer", "TForkingServer", "TThreadPoolServer"]
    @type  num_threads: int
    @param num_threads: TThreadPoolServer 사용시 띄울 thread 의 갯수
    @rtype: TServer, handler (Object)
    @return: 생성된 서버 인스턴스, 서버에 연결되어 실제 함수를 처리하는 인스턴스
    '''
    handler_instance = handler()
    processor_ = processor.Processor(handler_instance)
    transport = TSocket.TServerSocket(port)
    tfactory = TTransport.TBufferedTransportFactory()
    # tfactory = TTransport.TFramedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolAcceleratedFactory()

    # 서버를 어떻게 띄울 것인가?
    if server_type == "TThreadedServer":      # Thread per Connection
        server = TServer.TThreadedServer(processor_, transport, tfactory, pfactory)
    elif server_type == "TForkingServer":     # Process per Connection
        server = TServer.TForkingServer(processor_, transport, tfactory, pfactory)
    elif server_type == "TThreadPoolServer":  # Preloaded Thread with Pool
        server = TServer.TThreadPoolServer(processor_, transport, tfactory, pfactory)
        server.setNumThreads(num_threads)
    else:
        # No default
        raise Exception("Unknown Server Type")

    return server, handler_instance
