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

from arara import settings
from arara.server import *

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

from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

def connect_thrift_server(host, base_port, class_):
    transport = TSocket.TSocket(host, base_port + PORT[class_])
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
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


namespace = None

def get_namespace():
    global namespace
    if not namespace:
        namespace = Namespace()
    return namespace

# vim: set et ts=8 sw=4 sts=4
