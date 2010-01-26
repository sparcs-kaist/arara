import logging

from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

from arara import settings
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

HANDLER_MAPPING = [('login_manager', arara_thrift.LoginManager),
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


HANDLER_PORT = {'login_manager': 1,
        'member_manager': 2,
        'blacklist_manager': 3,
        'board_manager': 4,
        'read_status_manager': 5,
        'article_manager': 6,
        'messaging_manager': 7,
        'notice_manager': 8,
        'read_status_manager': 9,
        'search_manager': 10,
        'file_manager': 11,
        }

def connect(name):
    socket = TSocket.TSocket(settings.ARARA_SERVER_HOST,
                             settings.ARARA_SERVER_BASE_PORT + HANDLER_PORT[name])
    transport = TTransport.TBufferedTransport(socket)
    #transport = TTransport.TFramedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    #protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = dict(HANDLER_MAPPING)[name].Client(protocol)
    transport.open()
    logging.getLogger('get_server').info("Got server %s", name)
    return client


class Server(object):
    def __getattr__(self, name):
        if name in dict(HANDLER_MAPPING):
            return connect(name)
        raise AttributeError()


server = None


def get_server():
    global server
    if not server:
        server = Server()
    return server
