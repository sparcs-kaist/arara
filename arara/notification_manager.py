# -*- coding: utf-8 -*-
import time
import redis

from arara import arara_manager
from util import log_method_call_with_source
from etc import arara_settings
from arara_thrift.ttypes import Notification

log_method_call = log_method_call_with_source("noti_manager")

NOTI_EXPIRE_TIME = 2592000  # 30 days  TODO: subscribe now does not expire
TYPE_FROM_REPLY = 0
TYPE_FROM_SUBSCRIBE = 1

class NotiManager(arara_manager.ARAraManager):
    '''
    댓글 알림/구독 알림을 책임진다
    '''
    def __init__(self, engine):
        super(NotiManager, self).__init__(engine)
        # noti DB
        # DB No: 2
        # Key: user_id
        # Value: Ordered set of notification (score: timestamp, value: "type#reply_id#root_id")
        self.noti = redis.StrictRedis(host='127.0.0.1', port=arara_settings.REDIS_PORT, db=2)
        # noti-read-status DB
        # DB No: 3
        # Key: user_id
        # Value: timestamp repr that when user read last notification
        self.noti_read = redis.StrictRedis(host='127.0.0.1', port=arara_settings.REDIS_PORT, db=3)
        # article cache
        # DB No: 4
        # Key: "reply_id:title", "reply_id:author"
        self.article_cache = redis.StrictRedis(host='127.0.0.1', port=arara_settings.REDIS_PORT, db=4)
        # XXX: 중간에 글 제목이 바뀌었을 때에는 글 제목이 바뀐 후 첫 notification이 날아갈 때
        # 기존 notification.도 수정된 것처럼 보일 것이다. 하지만 큰 상관은 없을 듯.

        # subscribe DB
        # DB No: 5
        # Key: article_root_id
        # Value: Set of subscribed users
        self.sub_db = redis.StrictRedis(host='127.0.0.1', port=arara_settings.REDIS_PORT, db=5)

    def subscribe(self, session_key, article_id):
        '''
        @type  session_key: string
        @param session_key: 사용자 세션 키
        @type  article_id: int
        @param article_id: Root article의 id
        '''
        user_id = self.engine.login_manager.get_user_id(session_key)
        self.sub_db.sadd(article_id, user_id)

    def unsubscribe(self, session_key, article_id):
        '''
        @type  session_key: string
        @param session_key: 사용자 세션 키
        @type  article_id: int
        @param article_id: Root article의 id
        '''
        user_id = self.engine.login_manager.get_user_id(session_key)
        self.sub_db.srem(article_id, user_id)

    def is_subscribing(self, session_key, article_id):
        '''
        @type  session_key: string
        @param session_key: 사용자 세션 키
        @type  article_id: int
        @param article_id: Root article의 id
        @rtype: boolean
        @return: Whether user is subscribing given article or not
        '''
        user_id = self.engine.login_manager.get_user_id(session_key)
        return self.sub_db.sismember(article_id, user_id) and True or False

    def _publish(self, author_id, board_name, article_id, root_id, root_title, reply_author):
        '''
        모든 구독자에게 push를 보낸다. 이 명령은 반드시 Reply에 대한 Notification이
        먼저 등록된 후에 호출되어야 한다. 그렇지 않으면 중복이 생길 것이다.

        @type  author_id: int
        @param author_id: Reply 작성자 ID
        @type  board_name: string
        @type  board_name: 게시판 이름
        @type  article_id: int
        @param article_id: Update된 thread의 reply article id
        @type  root_id: int
        @param root_id: Update된 thread의 root id
        @type  root_title: string
        @param root_title: root article의 제목
        @type  reply_author: string
        @param reply_author: 달린 답글의 작성자 nickname. (만약 subscribe로 발생한 notification이면 empty string이어야 함.)
        '''

        # TODO: Pipelining
        for user_id in self.sub_db.smembers(root_id):
            # thread를 subscribe 했더라도 자신의 답글은 notification하지 않음
            if user_id == author_id:
                continue

            # If reply-notification already exists, pass.
            if not self.noti.zscore(user_id, '%d#%d#%d' % (TYPE_FROM_REPLY, article_id, root_id)):
                self.noti.zadd(user_id, time.time(), '%d#%d#%d' % (TYPE_FROM_SUBSCRIBE, article_id, root_id))

        self.article_cache.set('%d:board' % article_id, board_name)
        self.article_cache.expire('%d:board' % article_id, NOTI_EXPIRE_TIME)
        self.article_cache.set('%d:title' % article_id, root_title)
        self.article_cache.expire('%d:title' % article_id, NOTI_EXPIRE_TIME)
        self.article_cache.set('%d:author' % article_id, reply_author)
        self.article_cache.expire('%d:author' % article_id, NOTI_EXPIRE_TIME)

    def _add_noti(self, user_id, board_name, article_id, root_id, root_title, reply_author):
        '''
        Notification을 추가한다. Article Manager에서 쓰일 수 있다. session key가 아닌 user_id를
        받으므로 외부 Interface로 직접 쓰일 수는 없다.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        @type  board_name: string
        @type  board_name: 게시판 이름
        @type  article_id: int
        @param article_id: 달린 답글의 id
        @type  root_id: int
        @param root_id: Update된 thread의 root id
        @type  root_title: string
        @param root_title: root article의 제목
        @type  reply_author: string
        @param reply_author: 달린 답글의 작성자 nickname. (만약 subscribe로 발생한 notification이면 empty string이어야 함.)
        '''
        self.noti.zadd(user_id, time.time(), '%d#%d#%d' % (TYPE_FROM_REPLY, article_id, root_id))
        self.article_cache.set('%d:board' % article_id, board_name)
        self.article_cache.expire('%d:board' % article_id, NOTI_EXPIRE_TIME)
        self.article_cache.set('%d:title' % article_id, root_title)
        self.article_cache.expire('%d:title' % article_id, NOTI_EXPIRE_TIME)
        self.article_cache.set('%d:author' % article_id, reply_author)
        self.article_cache.expire('%d:author' % article_id, NOTI_EXPIRE_TIME)

    def get_noti(self, session_key, offset=0, length=10):
        '''
        noti를 적당히 가져와서 thrift type의 well formatted string을 반환한다.

        @type  session_key: string
        @param session_key: 사용자 세션 키
        @type  from_rank: int
        @param from_rank: from
        @type  to_rank: int
        @type  to_rank: to
        @rtype: list<ttypes.Notification>
        @return: List of Notification object
        '''
        # TODO: Pipelining
        user_id = self.engine.login_manager.get_user_id(session_key)

        # Avoid error when there is no redis server
        try:
            # EXPIRE TIME이 지난 것들을 삭제함
            self.noti.zremrangebyscore(user_id, "-inf", time.time() - NOTI_EXPIRE_TIME)
        except Exception:
            return []

        noti = self.noti.zrevrange(user_id, offset, offset+length-1, withscores=True, score_cast_func=float)

        last_read = self.noti_read.get(user_id) or 0.0
        last_read = float(last_read)

        # Last read time을 업데이트함
        self.noti_read.set(user_id, time.time())
        r = []

        for (value, score) in noti:
            n = Notification()
            n.type, n.article_id, n.root_id = map(int, value.split('#'))
            n.board_name = self.article_cache.get('%d:board' % n.article_id)
            n.root_title = self.article_cache.get('%d:title' % n.article_id)
            n.reply_author = self.article_cache.get('%d:author' % n.article_id)
            n.read = (score <= last_read)
            n.time = score

            r.append(n)

        return r

    __public__ = [
            subscribe,
            unsubscribe,
            is_subscribing,
            get_noti,
    ]
