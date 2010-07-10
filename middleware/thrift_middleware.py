from arara_thrift import ARAraThriftInterface

from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

from middleware import MANAGER_LIST

def connect_thrift_server(host, base_port):
    socket = TSocket.TSocket(host, base_port)
    transport = TTransport.TBufferedTransport(socket)
    #transport = TTransport.TFramedTransport(socket)

    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    #protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ARAraThriftInterface.Client(protocol)
    transport.open()
    return client

class Server(object):
    def __init__(self, host, base_port):
        self.host = host
        self.base_port = base_port

    def __getattr__(self, name):
        if name in set(MANAGER_LIST):
            return connect_thrift_server(self.host, self.base_port)
        raise AttributeError()
