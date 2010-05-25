import arara_thrift.LoginManager
import arara_thrift.ArticleManager
import arara_thrift.BlacklistManager
import arara_thrift.BoardManager
import arara_thrift.MemberManager
import arara_thrift.LoginManager
import arara_thrift.MessagingManager
import arara_thrift.NoticeManager
import arara_thrift.ReadStatusManager
import arara_thrift.SearchManager
import arara_thrift.FileManager

MAPPING = [('login_manager', arara_thrift.LoginManager),
           ('member_manager', arara_thrift.MemberManager),
           ('blacklist_manager', arara_thrift.BlacklistManager),
           ('board_manager', arara_thrift.BoardManager),
           ('read_status_manager', arara_thrift.ReadStatusManager),
           ('article_manager', arara_thrift.ArticleManager),
           ('messaging_manager', arara_thrift.MessagingManager),
           ('notice_manager', arara_thrift.NoticeManager),
           ('search_manager', arara_thrift.SearchManager),
           ('file_manager', arara_thrift.FileManager)
           ]

from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

from arara import settings

from middleware import HANDLER_PORT

def connect_thrift_server(host, base_port, class_):
    transport = TSocket.TSocket(host, base_port + HANDLER_PORT[class_])
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    client = dict(MAPPING)[class_].Client(protocol)
    transport.open()
    return client

def connect(name):
    socket = TSocket.TSocket(settings.ARARA_SERVER_HOST,
                             settings.ARARA_SERVER_BASE_PORT + HANDLER_PORT[name])
    transport = TTransport.TBufferedTransport(socket)
    #transport = TTransport.TFramedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    #protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = dict(MAPPING)[name].Client(protocol)
    transport.open()
    #logging.getLogger('get_server').info("Got server %s", name)
    return client


class Server(object):
    def __getattr__(self, name):
        if name in dict(MAPPING):
            return connect(name)
        raise AttributeError()
