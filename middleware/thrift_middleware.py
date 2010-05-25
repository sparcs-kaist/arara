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
