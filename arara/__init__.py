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

CLASSES = {'login_manager': LoginManager,
           'member_manager': MemberManager,
           'blacklist_manager': BlacklistManager,
           'board_manager': BoardManager,
           'readStatus_manager': ReadStatusManager,
           'article_manager': ArticleManager,
           'messaging_manager': MessagingManager,
           'notice_manager': NoticeManager,
           'read_status_manager': ReadStatusManager,
           'search_manager': SearchManager,
           'file_manager': FileManager,
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
