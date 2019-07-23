# -*- coding: utf-8 -*-
import datetime
import crypt
import time
import string
import random
import bcrypt

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.types import Boolean, DateTime, Integer, LargeBinary, PickleType, String, Text, Unicode, UnicodeText

from libs import smart_unicode

SALT_SET = string.lowercase + string.uppercase + string.digits + './'

Base = declarative_base()


class User(Base):
    __tablename__  = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    username = Column(Unicode(40), unique=True, index=True)
    password = Column(Unicode(80))
    password_reset = Column(Boolean)
    nickname = Column(Unicode(40), index=True)
    email = Column(Unicode(60), unique=True, index=True)
    signature = Column(Unicode(1024))
    self_introduction = Column(Unicode(1024))
    # ko_KR, en_US
    default_language = Column(Unicode(5))
    # Null, Seoul, Daejeon
    campus = Column(Unicode(15))
    activated = Column(Boolean)
    widget = Column(Integer)
    layout = Column(Integer)
    join_time = Column(DateTime)
    last_login_time = Column(DateTime)
    last_logout_time = Column(DateTime)
    last_login_ip = Column(Unicode(15))
    is_sysop = Column(Boolean)
    # 0 : 비회원 , 1 : 메일인증(non @kaist), 2 : 메일인증(@kaist), 3 : 포탈인증
    authentication_mode = Column(Integer)
    # 0 : LIST_ORDER_ROOT_ID , 1 : LIST_ORDER_LAST_REPLY_DATE
    listing_mode = Column(Integer)
    activated_backup = Column(Boolean)
    deleted = Column(Boolean)

    def __init__(self, username, password, nickname, email, signature,
                 self_introduction, default_language, campus):
        '''
        @type username: string
        @type password: string
        @type nickname: string
        @type email: string
        @type signature: string
        @type self_introduction: string
        @type default_language: string
        @type capus: string
        '''
        self.username = smart_unicode(username)
        self.password_reset = True
        self.set_password(password)
        self.nickname = smart_unicode(nickname)
        self.email = smart_unicode(email)
        self.signature = smart_unicode(signature)
        self.self_introduction = smart_unicode(self_introduction)
        self.default_language = smart_unicode(default_language)
        self.campus = smart_unicode(campus)
        self.activated = False
        self.widget = 0
        self.layout = 0
        self.join_time = datetime.datetime.fromtimestamp(time.time())
        self.last_login_time = None 
        self.last_logout_time = None
        self.last_login_ip = u''
        self.is_sysop = False
        self.authentication_mode = 0
        self.listing_mode = 0
        self.activated_backup = False
        self.deleted = False

    @classmethod
    def encrypt_password(cl, raw_password, salt, password_reset):
        '''
        @type raw_password: string
        @type salt: string
        '''

        if password_reset == False:
            pw = crypt.crypt(raw_password, salt)
            asc1 = pw[1:2]
            asc2 = pw[3:4]

            # XXX (combacsa): Temporary fix for strange pw values.
            #                 Don't know why "TypeError" occurs.
            i = ord('0') + ord('0')
            try:
                i = ord(asc1) + ord(asc2)
            except TypeError:
                pass
            while True:
                pw = crypt.crypt(pw, pw)
                i += 1
                if not(i % 13 != 0):
                    break
            
        else:
            salt = bcrypt.gensalt()
            raw_password = str(raw_password)
            pw = bcrypt.hashpw(raw_password, salt)

        return pw

    def crypt_password(self, raw_password):
        '''
        @type raw_password: string
        @rtype: string
        '''
        salt = ''.join(random.sample(SALT_SET, 2))
        return self.encrypt_password(raw_password, salt, self.password_reset)

    def set_password(self, password):
        '''
        @type password: string
        '''
        self.password_reset = True
        self.password = smart_unicode(self.crypt_password(password))

    def compare_password(self, password):
        '''
        @type password: string
        @rtype: bool
        '''
        if self.password_reset == False:
            hash_from_user = self.encrypt_password(password, self.password, self.password_reset)
            hash_from_db = self.password
            hash_from_user = smart_unicode(hash_from_user.strip())
            hash_from_db = smart_unicode(hash_from_db.strip())

            return hash_from_user == hash_from_db

        else:
            pwd_from_user = str(password)
            pwd_from_db = str(self.password)

            return bcrypt.checkpw(pwd_from_user, pwd_from_db)

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.username, self.nickname)


class UserActivation(Base):
    __tablename__  = 'user_activation'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    activation_code = Column(Unicode(50), unique=True)
    issued_date = Column(DateTime)

    user = relationship(User, backref='activation', uselist=False)

    def __init__(self, user, activation_code):
        '''
        @type user: model.User
        @type activation_code: string
        '''
        self.user = user
        self.activation_code = smart_unicode(activation_code)
        self.issued_date = datetime.datetime.fromtimestamp(time.time())

    def __repr__(self):
        return "<UserActivation('%s', '%s')>" % (self.user.username, self.activation_code)


class Category(Base):
    __tablename__  = 'categories'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    category_name = Column(Unicode(30), unique=True, index=True)
    order = Column(Integer, nullable=True)

    def __init__(self, category_name, order):
        '''
        @type category_name: string
        @type order: int
        '''
        self.category_name = smart_unicode(category_name)
        self.order = order

    def __repr__(self):
        return "<Category('%s')>" % (self.category_name)


BOARD_TYPE_NORMAL = 0
BOARD_TYPE_PICTURE = 1
BOARD_TYPE_ANONYMOUS = 2

class Board(Base):
    __tablename__  = 'boards'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id          = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    board_name  = Column(Unicode(30), unique=True, index=True)
    board_alias = Column(Unicode(30), unique=True)
    board_description = Column(Unicode(300))
    deleted   = Column(Boolean)
    read_only = Column(Boolean)
    hide      = Column(Boolean)
    type      = Column(Integer)
    order     = Column(Integer, nullable=True, index=True)
    to_read_level  = Column(Integer)
    to_write_level = Column(Integer)

    category = relationship(Category, backref='boards')

    def __init__(self, board_name, board_alias, board_description, order, category, type=BOARD_TYPE_NORMAL, to_read_level=3, to_write_level=3, anonymous=False):
        '''
        @type board_name: string
        @type board_description: string
        @type order: int
        @type category: model.Category
        @type type: int
        @type to_read_level: int (0: 비회원, 1: 메일인증(non-@kaist), 2: 메일인증(@kaist), 3: 포탈인증)
        @type to_write_level: int (0: 비인증, 1: 메일인증(non-@kaist), 2: 메일인증(@kaist), 3: 포탈인증)
        '''
        self.board_name = smart_unicode(board_name)
        self.board_alias = smart_unicode(board_alias)
        self.board_description = smart_unicode(board_description)
        self.deleted = False
        self.read_only = False
        self.hide = False
        self.order = order
        self.category = category
        self.type = type
        self.to_read_level = to_read_level
        self.to_write_level = to_write_level

    def __repr__(self):
        return "<Board('%s', '%s', '%s')>" % (self.board_name, self.board_alias, self.board_description)


class BBSManager(Base):
    __tablename__  = 'bbs_managers'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    board_id = Column(Integer, ForeignKey('boards.id'))
    manager_id = Column(Integer, ForeignKey('users.id'))

    board = relationship(Board, backref='management', lazy=True)
    manager = relationship(User, backref='managing_board', lazy=True)

    def __init__(self, board, manager):
        '''
        @type board: model.Board
        @type manager: model.User
        '''
        self.board = board
        self.manager = manager

    def __repr__(self):
        return "<BBSManager('%s', '%s')>" % (self.board, self.manager)


class BoardHeading(Base):
    __tablename__  = 'board_headings'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    board_id = Column(Integer, ForeignKey('boards.id'), index=True)
    heading = Column(Unicode(30))

    board = relationship(Board, backref='headings', lazy=False)

    def __init__(self, board, heading):
        '''
        @type board: model.Board
        @type heading: string
        '''
        self.board = board
        self.heading = smart_unicode(heading)

    def __repr__(self):
        return "<BoardHeading('%s', '%s')>" % (self.board, self.heading)


class Article(Base):
    __tablename__  = 'articles'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    # 사용자가 작성한 내용물
    id      = Column(Integer, primary_key=True)
    title   = Column(Unicode(200))
    content = Column(UnicodeText)
    date    = Column(DateTime)

    # 게시물이 속하는 곳
    board_id = Column(Integer, ForeignKey('boards.id'), index=True)
    # TODO: nullable=True 는 어디까지나 임시방편이므로 어서 지운다.
    heading_id = Column(Integer, ForeignKey('board_headings.id'), nullable=True)

    # 게시자 정보
    author_id = Column(Integer, ForeignKey('users.id'))
    author_nickname = Column(Unicode(40))
    author_ip = Column(Unicode(15))

    # 반응
    hit = Column(Integer)
    positive_vote = Column(Integer)
    negative_vote = Column(Integer)

    # 플래그
    deleted = Column(Boolean)
    destroyed = Column(Boolean)
    is_searchable = Column(Boolean, nullable=False)

    # 다른 글과의 관계
    root_id = Column(Integer, ForeignKey('articles.id'), nullable=True)
    parent_id = Column(Integer, ForeignKey('articles.id'), nullable=True)
    reply_count = Column(Integer, nullable=False)
    last_reply_id = Column(Integer)
    last_reply_date = Column(DateTime)
    last_modified_date = Column(DateTime, index=True)

    # 맵핑
    author  = relationship(User, backref='articles', lazy=False)
    board   = relationship(Board, backref='articles', lazy=False)
    heading = relationship(BoardHeading, backref='articles', lazy=False)

    children = relationship('Article', join_depth=3,
        primaryjoin='articles.c.parent_id == articles.c.id',
        order_by='articles.c.id',
        backref=backref('parent', lazy=True,
            remote_side=[id],
            primaryjoin='articles.c.parent_id == articles.c.id'))

    descendants = relationship('Article', lazy=True,
        primaryjoin='articles.c.root_id == articles.c.id',
        backref=backref('root',
            remote_side=[id],
            primaryjoin='articles.c.root_id == articles.c.id'))

    def __init__(self, board, heading, title, content, author, author_ip, parent):
        '''
        @type board: model.Board
        @type heading: model.BoardHeading
        @type title: string
        @type content: string
        @type author: model.User
        @type author_ip: string
        @type parent: model.Article
        '''
        self.board = board
        self.heading = heading
        self.title = smart_unicode(title)
        self.content = smart_unicode(content)
        self.author = author
        self.author_nickname = author.nickname
        self.author_ip = smart_unicode(author_ip)
        self.deleted = False
        self.date = datetime.datetime.fromtimestamp(time.time())
        self.hit = 0
        self.positive_vote = 0
        self.negative_vote = 0
        self.reply_count = 0
        self.is_searchable = True
        if parent:
            if parent.root:
                self.root = parent.root
            else:
                self.root = parent
        else:
            self.root = None
        self.parent = parent
        self.last_modified_date = self.date
        self.destroyed = False
        self.last_reply_date = self.date

    def __repr__(self):
        return "<Article('%s', '%s', %s)>" % (self.title, self.author.username, str(self.date))

class BoardNotice(Base):
    __tablename__  = 'board_notice'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    article_id = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    article = relationship(Article, backref=None, lazy=True)

    def __init__(self, article):
        '''
        @type article: model.Article
        '''
        self.article = article

class ArticleVoteStatus(Base):
    __tablename__  = 'article_vote_status'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    board_id = Column(Integer, ForeignKey('boards.id'), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    article = relationship(Article, backref='voted_users', lazy=True)
    user = relationship(User, backref='voted_articles', lazy=True)
    board = relationship(Board, backref=None, lazy=True)

    def __init__(self, user, board, article):
        '''
        @type user: model.User
        @type board: model.Board
        @type article: model.Article
        '''
        self.user = user
        self.board = board
        self.article = article


class ReadStatus(Base):

    class MyPickleType(PickleType):
        impl = LargeBinary(length=2 ** 30)

    __tablename__  = 'read_status'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    read_status_data = Column(MyPickleType)
    read_status_numbers = Column(LargeBinary(length=2 ** 30))
    read_status_markers = Column(LargeBinary(length=2 ** 30))

    user = relationship(User, backref='read_status')

    def __init__(self, user, read_status_data):
        '''
        @type user: model.User
        @type read_status_data: read_status_manager.ReadStatus
        '''
        self.user = user
        self.read_status_data = None
        self.read_status_numbers = ''
        self.read_status_markers = ''

    def __repr__(self):
        return "<ReadStatus('%s', '%s')>" % (self.user.username, self.read_status_data)

class ScrapStatus(Base):
    __tablename__  = 'scrap_status'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)

    user = relationship(User, backref='scrapped_articles', lazy=True)
    article = relationship(Article, backref='scrapped_users', lazy=True)

    def __init__(self, user, article):
        '''
        @type user: model.User
        @type article: model.Article
        '''
        self.user = user
        self.article = article

    def __repr__(self):
        return "<ScrapStatus('%s', '%s')>" % (self.user.username, self.article.title)

class Blacklist(Base):
    __tablename__  = 'blacklists'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    blacklisted_user_id = Column(Integer, ForeignKey('users.id'))
    blacklisted_date = Column(DateTime)
    last_modified_date = Column(DateTime)
    block_article = Column(Boolean)
    block_message = Column(Boolean)

    user = relationship(User, lazy=False,
            primaryjoin='blacklists.c.user_id == users.c.id',
            backref=backref('blacklist', lazy=True, join_depth=1,
                    primaryjoin='blacklists.c.user_id == users.c.id',
                    viewonly=True))
    target_user = relationship(User, lazy=False,
            primaryjoin='blacklists.c.blacklisted_user_id == users.c.id',
            backref=backref('blacklisted', lazy=True, join_depth=1,
                    primaryjoin='blacklists.c.blacklisted_user_id == users.c.id',
                    viewonly=True))

    def __init__(self, user, target_user, block_article, block_message):
        '''
        @type user: model.User
        @type target_user: model.User
        @type block_article: bool
        @type block_message: bool
        '''
        self.user = user 
        self.target_user = target_user
        self.block_article = block_article
        self.block_message = block_message
        self.blacklisted_date = datetime.datetime.fromtimestamp(time.time())
        self.last_modified_date = self.blacklisted_date

    def __repr__(self):
        return "<Blacklist('%s','%s')>" % (self.user.username, self.target_user.username) 


class Message(Base):
    __tablename__  = 'messages'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    from_ip = Column(Unicode(15))
    to_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    sent_time = Column(DateTime)
    message = Column(Unicode(1000))
    received_deleted = Column(Boolean)
    sent_deleted = Column(Boolean)
    read_status = Column(Unicode(1))

    from_user = relationship(User, primaryjoin='messages.c.from_id == users.c.id',
            backref=backref('send_messages', lazy=True, join_depth=1,
                    primaryjoin='messages.c.from_id == users.c.id',
                    viewonly=False))
    to_user = relationship(User, primaryjoin='messages.c.to_id == users.c.id',
            backref=backref('received_messages', lazy=True, join_depth=1,
                    primaryjoin='messages.c.to_id == users.c.id',
                    viewonly=False))

    def __init__(self, from_user, from_user_ip, to_user, message):
        '''
        @type from_user: model.User
        @type from_user_ip: string
        @type to_user: model.User
        @type mesage: string
        '''
        self.from_user = from_user
        self.from_user_ip = smart_unicode(from_user_ip)
        self.to_user = to_user
        self.sent_time = datetime.datetime.fromtimestamp(time.time())
        self.message = smart_unicode(message)
        self.received_deleted = False
        self.sent_deleted = False
        self.read_status = u'N'

    def __repr__(self):
        return "<Message('%s','%s','%s')>" % (self.from_user, self.to_user, self.message)


class Banner(Base):
    __tablename__  = 'banners'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    content = Column(UnicodeText)
    issued_date = Column(DateTime)
    due_date = Column(DateTime)
    valid = Column(Boolean)
    weight = Column(Integer)

    def __init__(self, content, weight, due_date):
        '''
        @type content: string
        @type weight: int
        @type due_date: datetime
        '''
        self.content = smart_unicode(content)
        self.valid = False
        self.weight = weight
        self.issued_date = datetime.datetime.fromtimestamp(time.time()) 
        self.due_date = due_date 

    def __repr__(self):
        return "<Banner('%s','%s')>" % (self.content, self.valid)


class Welcome(Base):
    __tablename__  = 'welcomes'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    content = Column(UnicodeText)
    issued_date = Column(DateTime)
    due_date = Column(DateTime)
    valid = Column(Boolean)
    weight = Column(Integer)

    def __init__(self, content, weight, due_date):
        '''
        @type content: string
        @type weight: int
        @type due_date: datetime
        '''
        self.content = smart_unicode(content)
        self.valid = True
        self.weight = weight
        self.issued_date = datetime.datetime.fromtimestamp(time.time()) 
        self.due_date = due_date 

    def __repr__(self):
        return "<Welcome('%s','%s')>" % (self.content, self.valid)


class File(Base):
    __tablename__  = 'files'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    filename = Column(Unicode(200))
    saved_filename = Column(Unicode(200))
    filepath = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    board_id = Column(Integer, ForeignKey('boards.id'), index=True)
    article_id = Column(Integer, ForeignKey('articles.id'), index=True)
    deleted = Column(Boolean)

    user = relationship(User, backref='files', lazy=True)
    board = relationship(Board, backref=None, lazy=True)
    article = relationship(Article, backref=None, lazy=True)

    def __init__(self, filename, saved_filename, filepath, user, board, article):
        '''
        @type filename: string
        @type saved_filename: string
        @type filepath: string
        @type user: model.User
        @type board: model.Board
        @type article: model.Article
        '''
        # TODO: 왜 이렇게 많은 정보가 필요하지?
        self.filename = smart_unicode(filename)
        self.saved_filename = smart_unicode(saved_filename)
        self.filepath= filepath 
        self.user = user
        self.board = board
        self.article = article
        self.deleted = False

    def __repr__(self):
        return "<File('%s')>" % (self.filename)


class Visitor(Base):
    __tablename__  = 'visitors'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    total = Column(Integer, primary_key=True)
    today = Column(Integer)
    date = Column(DateTime)

    def __init__(self):
        self.total = 0
        self.today = 0
        self.date = datetime.datetime.fromtimestamp(time.time())

    def __repr__(self):
        return "<Visitor<'%d','%d'>" % (self.total, self.today)

class Link(Base):
    __tablename__  = 'links'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    link_name = Column(Unicode(30), unique=True)
    link_description = Column(Unicode(300))
    link_url = Column(Unicode(100))
    ishidden = Column(Boolean)
    deleted = Column(Boolean)
    order = Column(Integer)

    def __init__(self, link_name, link_description, link_url, order):
        '''
        @type link_name: string
        @type link_description: string
        @type link_url: string
        @type order: int
        '''
        self.link_name = smart_unicode(link_name)
        self.link_description = smart_unicode(link_description)
        self.link_url = smart_unicode(link_url)
        self.ishidden = False
        self.deleted = False
        self.order = order

    def __repr__(self):
        return "<Link('%s', '%s', '%s')>" % (self.link_name, self.link_description, self.link_url)


class SelectedBoards(Base):
    __tablename__  = 'selected_boards'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    board_id = Column(Integer, ForeignKey('boards.id'))

    user = relationship(User, lazy=False,
            primaryjoin='selected_boards.c.user_id == users.c.id',
            backref=backref('selected_boards', lazy=True, join_depth=1,
                    primaryjoin='selected_boards.c.user_id == users.c.id',
                    viewonly=True))
    board = relationship(Board, None, lazy=True)

    def __init__(self, user, board):
        '''
        @type user: model.User 
        @type board: model.Board
        '''
        self.user = user
        self.board = board

    def __repr__(self):
        return "<SelectedBoards('%s')>" % (self.board)


class LoginSession(Base):
    __tablename__ = 'login_sessions'
    __table__args = {'mysql_engine': 'InnoDB'}

    session_key = Column(String(40), primary_key=True)
    session_data = Column(PickleType)
    expire_date = Column(DateTime, index=True)

    def __init__(self, session_key, session_data, expire_date):
        '''
        @type session_key: str
        @type session_data: object
        @type expire_date: datetime.datetime
        '''
        self.session_key = session_key
        self.session_data = session_data
        self.expire_date = expire_date

class LostPasswordToken(Base):
    __tablename__ = 'lost_password_token'
    __table__args = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    code = Column(String(25))

    user = relationship(User, lazy=False,
            primaryjoin='lost_password_token.c.user_id == users.c.id',
            backref=backref('lost_password_token', lazy=True, join_depth=1,
                    primaryjoin='lost_password_token.c.user_id == users.c.id',
                    viewonly=True))

Index('articles_board_and_id', Article.__table__.c.board_id)
Index('articles_board_and_last_reply_id', Article.__table__.c.board_id, Article.__table__.c.last_reply_id)
Index('votes_user_and_board_and_article', ArticleVoteStatus.__table__.c.board_id, ArticleVoteStatus.__table__.c.article_id, ArticleVoteStatus.__table__.c.user_id)
Index('blacklisted_user_and_user', Blacklist.__table__.c.user_id, Blacklist.__table__.c.blacklisted_user_id)


engine = None
pool = None


def get_engine():
    '''
    Database 연결을 하기 위한 connector.
    etc/arara_settings.py 에 지정한 DB 연결방식대로 DB 에 접속한다.

    mysql / sqlite / 그 밖에 사용자가 직접 SQLAlchemy 에게 넘겨주는 접속 string으로.
    '''
    global engine
    global pool
    if engine:
        return engine

    from etc import arara_settings
    CONNECTION_STRING = None
    SQLALCHEMY_KWARGS = None
    # creating DB Connection String
    if arara_settings.ARARA_DBTYPE == 'mysql':
        CONNECTION_STRING = 'mysql://%s:%s@%s/%s?charset=utf8&use_unicode=1' % \
            (arara_settings.MYSQL_ID,
             arara_settings.MYSQL_PASSWD,
             arara_settings.MYSQL_DBHOST,
             arara_settings.MYSQL_DBNAME)
        SQLALCHEMY_KWARGS = {'encoding': 'utf-8',
                             'convert_unicode': True,
                             'assert_unicode': False,
                             'pool_size': 300,
                             'max_overflow': 10,
                             'pool_recycle': 5,
                             'echo': False,
                             'echo_pool': False}
        # (pipoket) Note: To see what`s happing to the pool, turn on echo_pool above.
    elif arara_settings.ARARA_DBTYPE == 'sqlite':
        CONNECTION_STRING = 'sqlite:///%s' % arara_settings.SQLITE_PATH
        SQLALCHEMY_KWARGS = {'encoding': 'utf-8',
                             'convert_unicode': True,
                             'assert_unicode': None,
                             'poolclass': NullPool}
    elif arara_settings.ARARA_DBTYPE == 'other':
        CONNECTION_STRING = arara_settings.DB_CONNECTION_STRING
        SQLALCHEMY_KWARGS = {'encoding': 'utf-8',
                             'convert_unicode': True,
                             'assert_unicode': None}
    else:
        # No other DB support.
        assert False, "DB Type must be either one of mysql, sqlite, or other."

    engine = create_engine(CONNECTION_STRING, **SQLALCHEMY_KWARGS)
    pool = engine.pool
    return engine

Session = None

def init_database():
    '''
    Database 와 여기에 접속할 수 있는 Session 을 만든다.
    '''
    global Session
    get_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)

def init_test_database():
    '''
    TEST 를 위한 Database 를 메모리 상에 만든다. 물론 Session 도.
    '''
    global engine, Session
    engine = create_engine('sqlite://', convert_unicode=True, encoding='utf-8', echo=False)
    Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)
    Base.metadata.create_all(engine)
