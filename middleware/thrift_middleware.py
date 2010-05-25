from arara.article_manager import ArticleManager
from arara.blacklist_manager import BlacklistManager
from arara.board_manager import BoardManager
from arara.member_manager import MemberManager
from arara.login_manager import LoginManager
from arara.messaging_manager import MessagingManager
from arara.notice_manager import NoticeManager
from arara.read_status_manager import ReadStatusManager
from arara.search_manager import SearchManager
from arara.file_manager import FileManager

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

MAPPING = [(LoginManager, arara_thrift.LoginManager),
           (MemberManager, arara_thrift.MemberManager),
           (BlacklistManager, arara_thrift.BlacklistManager),
           (BoardManager, arara_thrift.BoardManager),
           (ReadStatusManager, arara_thrift.ReadStatusManager),
           (ArticleManager, arara_thrift.ArticleManager),
           (MessagingManager, arara_thrift.MessagingManager),
           (NoticeManager, arara_thrift.NoticeManager),
           (SearchManager, arara_thrift.SearchManager),
           (FileManager, arara_thrift.FileManager)
           ]

from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

from arara import PORT

def connect_thrift_server(host, base_port, class_):
    transport = TSocket.TSocket(host, base_port + PORT[class_])
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    client = dict(MAPPING)[class_].Client(protocol)
    transport.open()
    return client

from arara import settings

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

def connect(name):
    socket = TSocket.TSocket(settings.ARARA_SERVER_HOST,
                             settings.ARARA_SERVER_BASE_PORT + HANDLER_PORT[name])
    transport = TTransport.TBufferedTransport(socket)
    #transport = TTransport.TFramedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    #protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = dict(HANDLER_MAPPING)[name].Client(protocol)
    transport.open()
    #logging.getLogger('get_server').info("Got server %s", name)
    return client


class Server(object):
    def __getattr__(self, name):
        if name in dict(HANDLER_MAPPING):
            return connect(name)
        raise AttributeError()
