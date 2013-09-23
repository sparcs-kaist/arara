#-*- coding: utf-8 -*-
from arara.article_manager import ArticleManager
from arara.blacklist_manager import BlacklistManager
from arara.board_manager import BoardManager
from arara.member_manager import MemberManager
from arara.login_manager import LoginManager
from arara.messaging_manager import MessagingManager
from arara.notice_manager import NoticeManager
from arara.search_manager import SearchManager
from arara.file_manager import FileManager
from arara.bot_manager import BotManager
from arara.notification_manager import NotiManager
from etc import arara_settings

class ARAraEngine(object):
    '''
    하나의 서버에서 돌아가는 아라라 엔진 인스턴스.
    각 매니저 인스턴스들을 보유하고 있다.
    '''
    # TODO: 아래의 모든 "mapping" 을 독립적인 함수로 옮기자.
    # TODO: 이 클래스를 위한 TEST 는 설계할 수 있는가?

    def __init__(self):
        self.login_manager = LoginManager(self)
        self.member_manager = MemberManager(self)
        self.blacklist_manager = BlacklistManager(self)
        self.board_manager = BoardManager(self)

        if arara_settings.READ_STATUS_STORE_TYPE == 'maindb':
            from arara.read_status.db_backend import ReadStatusManagerDB
            self.read_status_manager = ReadStatusManagerDB(self)
        elif arara_settings.READ_STATUS_STORE_TYPE == 'redis':
            from arara.read_status.redis_backend import ReadStatusManagerRedis
            self.read_status_manager = ReadStatusManagerRedis(self)
        else:
            from arara.read_status.default_backend import ReadStatusManagerDefault
            self.read_status_manager = ReadStatusManagerDefault(self)

        self.article_manager = ArticleManager(self)
        self.messaging_manager = MessagingManager(self)
        self.notice_manager = NoticeManager(self)
        self.search_manager = SearchManager(self)
        self.file_manager = FileManager(self)
        self.bot_manager = BotManager(self)
        self.noti_manager = NotiManager(self)

    def shutdown(self):
        '''
        엔진이 종료될 때 반드시 수행되어야 하는 동작들을 이행한다.
        '''
        # TODO: 필요한 동작들이 무엇일지 잘 생각해 보자.
        self.login_manager.shutdown()
