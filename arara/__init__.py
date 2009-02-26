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
           (ReadStatusManager, arara_thrift.ReadStatusManager),
           (SearchManager, arara_thrift.SearchManager),
           (FileManager, arara_thrift.FileManager)
           ]

DEPENDENCY = {LoginManager: [MemberManager],
              MemberManager: [LoginManager],
              BlacklistManager: [MemberManager, LoginManager],
              BoardManager: [LoginManager],
              ReadStatusManager: [LoginManager, MemberManager],
              ArticleManager: [LoginManager, BlacklistManager,
                               ReadStatusManager, BoardManager,
                               FileManager],
              MessagingManager: [LoginManager, MemberManager,
                                 BlacklistManager],
              NoticeManager: [LoginManager, MemberManager],
              ReadStatusManager: [LoginManager, MemberManager],
              SearchManager: [BoardManager, LoginManager],
              FileManager: [LoginManager]
              }

PORT = {LoginManager: 1,
        MemberManager: 2,
        BlacklistManager: 3,
        BoardManager: 4,
        ReadStatusManager: 5,
        ArticleManager: 6,
        MessagingManager: 7,
        NoticeManager: 8,
        ReadStatusManager: 9,
        SearchManager: 10,
        FileManager: 11,
        }

CLASSES = {'LoginManager': LoginManager,
           'MemberManager': MemberManager,
           'BlacklistManager': BlacklistManager,
           'BoardManager': BoardManager,
           'ReadStatusManager': ReadStatusManager,
           'ArticleManager': ArticleManager,
           'MessagingManager': MessagingManager,
           'NoticeManager': NoticeManager,
           'ReadStatusManager': ReadStatusManager,
           'SearchManager': SearchManager,
           'FileManager': FileManager,
        }

ARARA_SERVER_HOST = 'localhost'
ARARA_SERVER_BASE_PORT = 8000

from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer
def connect_thrift_server(host, base_port, class_):
    transport = TSocket.TSocket(host, base_port + PORT[class_])
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = dict(MAPPING)[class_].Client(protocol)
    transport.open()
    return client


class Namespace(object):
    def __init__(self):
        self.login_manager = LoginManager()
        self.member_manager = MemberManager()
        self.login_manager._set_member_manager(self.member_manager)
        self.member_manager._set_login_manager(self.login_manager)
        self.blacklist_manager = BlacklistManager()
        self.blacklist_manager._set_member_manager(self.member_manager)
        self.blacklist_manager._set_login_manager(self.login_manager)
        self.board_manager = BoardManager()
        self.board_manager._set_login_manager(self.login_manager)
        self.read_status_manager = ReadStatusManager()
        self.read_status_manager._set_login_manager(self.login_manager)
        self.read_status_manager._set_member_manager(self.member_manager)
        self.article_manager = ArticleManager()
        self.article_manager._set_login_manager(self.login_manager)
        self.article_manager._set_blacklist_manager(self.blacklist_manager)
        self.article_manager._set_read_status_manager(self.read_status_manager)
        self.article_manager._set_board_manager(self.board_manager)
        self.messaging_manager = MessagingManager()
        self.messaging_manager._set_login_manager(self.login_manager)
        self.messaging_manager._set_member_manager(self.member_manager)
        self.messaging_manager._set_blacklist_manager(self.blacklist_manager)
        self.notice_manager = NoticeManager()
        self.notice_manager._set_login_manager(self.login_manager)
        self.notice_manager._set_member_manager(self.member_manager)
        self.read_status_manager = ReadStatusManager()
        self.read_status_manager._set_login_manager(self.login_manager)
        self.read_status_manager._set_member_manager(self.member_manager)
        self.search_manager = SearchManager()
        self.search_manager._set_board_manager(self.board_manager)
        self.search_manager._set_login_manager(self.login_manager)
        self.file_manager = FileManager()
        self.file_manager._set_login_manager(self.login_manager)
        self.article_manager._set_file_manager(self.file_manager)


class Server(object):
    def __init__(self):
        def connect(class_):
            return connect_thrift_server(ARARA_SERVER_HOST,
                                         ARARA_SERVER_BASE_PORT,
                                         class_)
        self.login_manager = connect(LoginManager)
        self.member_manager = connect(MemberManager)
        self.blacklist_manager = connect(BlacklistManager)
        self.board_manager = connect(BoardManager)
        self.read_status_manager = connect(ReadStatusManager)
        self.article_manager = connect(ArticleManager)
        self.messaging_manager = connect(MessagingManager)
        self.notice_manager = connect(NoticeManager)
        self.search_manager = connect(SearchManager)
        self.file_manager = connect(FileManager)

namespace = None
server = None

def get_namespace():
    global namespace
    if not namespace:
        namespace = Namespace()
    return namespace

def get_server():
    global server
    if not server:
        server = Server()
    return server

# vim: set et ts=8 sw=4 sts=4
