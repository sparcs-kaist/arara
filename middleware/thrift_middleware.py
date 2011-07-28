#-*- coding: utf-8 -*-
from arara_thrift import ARAraThriftInterface

from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

from middleware import MANAGER_LIST

MANAGER_LIST = set(MANAGER_LIST)

def connect_thrift_server(host, base_port):
    '''
    @type  host: string
    @param host: Thrift 서버의 주소
    @type  base_port: int
    @param base_port: Thrift 서버의 포트번호 시작점
    @rtype: Thrift Client Instance
    @return: Thrift Middleware 에 연결된 Client Instance
    '''
    socket = TSocket.TSocket(host, base_port)
    transport = TTransport.TBufferedTransport(socket)
    #transport = TTransport.TFramedTransport(socket)

    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    #protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ARAraThriftInterface.Client(protocol)
    transport.open()
    return client

class Server(object):
    '''
    Thrift Middleware 에 접속하여 각 Manager 의 함수를 호출하게 해 준다.

    >>> s = Server('127.0.0.1', 10000)
    >>> s.login_manager.login('ID', 'PW', '127.0.0.1')

    사용법: 호출하고자 하는 method 가 있는 manager 의 이름을 함께 지정한다.
    그러면 능동적으로 해당 manager 가 있는 Middleware Port 로 연결해 준다.

    changeset fa96e4727daa 에서 모든 Manager 가 한 서버로 통합되었기 때문에,
    현재의 코드에는 각각의 manager 에 따라 다른 port 로 연결해주는 기능이 없다.
    '''
    def __init__(self, host, base_port):
        '''
        @type  host: string
        @param host: Thrift 서버의 주소
        @type  base_port: int
        @param base_port: Thrift 서버의 포트번호 시작점
        '''
        self.host = host
        self.base_port = base_port

    def __getattr__(self, name):
        '''
        @type  name: string
        @param name: 호출하고자 하는 Manager 의 이름
        @rtype: Thrift Client Instance
        @return: 호출하려는 함수가 있는 Manager 와 연결된 Client Instance
        '''
        if name in MANAGER_LIST:
            return connect_thrift_server(self.host, self.base_port)
        raise AttributeError()
