#-*- coding: utf-8 -*-
# TODO: 이 파일의 "목적성" 이 불분명해졌다.
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
from arara.bot_manager import BotManager

from arara.arara_engine import ARAraEngine

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
           'bot_manager': BotManager,
        }

# vim: set et ts=8 sw=4 sts=4
