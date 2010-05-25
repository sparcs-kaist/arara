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

from arara import settings
from arara.server import get_server

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

class Namespace(object):
    def __init__(self):
        self.login_manager = LoginManager()
        self.member_manager = MemberManager()
        self.blacklist_manager = BlacklistManager()
        self.board_manager = BoardManager()
        self.read_status_manager = ReadStatusManager()
        self.article_manager = ArticleManager()
        self.messaging_manager = MessagingManager()
        self.notice_manager = NoticeManager()
        self.read_status_manager = ReadStatusManager()
        self.search_manager = SearchManager()
        self.file_manager = FileManager()

namespace = None

def get_namespace():
    global namespace
    if not namespace:
        namespace = Namespace()
    return namespace

# vim: set et ts=8 sw=4 sts=4
