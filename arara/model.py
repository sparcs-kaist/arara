# -*- coding: utf-8 -*-
import datetime
import crypt
import time
import md5
import string
import random

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.databases.mysql import MSLongBlob

def smart_unicode(string):
    # TODO: util.py 나 적당한 곳으로 옮긴다. util.py 에 있지 않나?
    if type(string) == str:
        return unicode(string, 'UTF-8', 'replace')
    else:
        return unicode(string)

SALT_SET = string.lowercase + string.uppercase + string.digits + './'

class User(object):
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

    @classmethod
    def encrypt_password(cl, raw_password, salt):
        '''
        @type raw_password: string
        @type salt: string
        '''
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

        return pw

    def crypt_password(self, raw_password):
        '''
        @type raw_password: string
        @rtype: string
        '''
        salt = ''.join(random.sample(SALT_SET, 2))
        return self.encrypt_password(raw_password, salt)

    def set_password(self, password):
        '''
        @type password: string
        '''
        self.password = smart_unicode(self.crypt_password(password))

    def compare_password(self, password):
        '''
        @type password: string
        @rtype: boolean
        '''
        hash_from_user = self.encrypt_password(password, self.password)
        hash_from_db = self.password
        hash_from_user = smart_unicode(hash_from_user.strip())
        hash_from_db = smart_unicode(hash_from_db.strip())
        return hash_from_user == hash_from_db

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.username, self.nickname)

class BBSManager(object):
    def __init__(self, board, manager):
        '''
        @type board: model.Board
        @type manager: model.User
        '''
        self.board = board
        self.manager = manager

    def __repr__(self):
        return "<BBSManager('%s', '%s')>" % (self.board, self.manager)

class UserActivation(object):
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

class Category(object):
    def __init__(self, category_name):
        '''
        @type category_name: string
        '''
        self.category_name = smart_unicode(category_name)

    def __repr__(self):
        return "<Category('%s')>" % (self.category_name)

class Board(object):
    def __init__(self, board_name, board_description, order, category):
        '''
        @type board_name: string
        @type board_description: string
        @type order: int
        @type category: model.Category
        '''
        self.board_name = smart_unicode(board_name)
        self.board_description = smart_unicode(board_description)
        self.deleted = False
        self.read_only = False
        self.hide = False
        self.order = order
        self.category = category

    def __repr__(self):
        return "<Board('%s', '%s')>" % (self.board_name, self.board_description)

class Link(object):
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

class BoardHeading(object):
    def __init__(self, board, heading):
        '''
        @type board: model.Board
        @type heading: string
        '''
        self.board = board
        self.heading = smart_unicode(heading)

    def __repr__(self):
        return "<BoardHeading('%s', '%s')>" % (self.board, self.heading)

class Article(object):
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

class ArticleVoteStatus(object):
    def __init__(self, user, board, article):
        '''
        @type user: model.User
        @type board: model.Board
        @type article: model.Article
        '''
        self.user = user
        self.board = board
        self.article = article

class ReadStatus(object):
    def __init__(self, user, read_status_data):
        '''
        @type user: model.User
        @type read_status_data: read_status_manager.ReadStatus
        '''
        self.user = user
        self.read_status_data = read_status_data

    def __repr__(self):
        return "<ReadStatus('%s', '%s')>" % (self.user.username, self.read_status_data)

class Blacklist(object):
    def __init__(self, user, target_user, block_article, block_message):
        '''
        @type user: model.User
        @type target_user: model.User
        @type block_article: boolean
        @type block_message: boolean
        '''
        self.user = user 
        self.target_user = target_user
        self.block_article = block_article
        self.block_message = block_message
        self.blacklisted_date = datetime.datetime.fromtimestamp(time.time())
        self.last_modified_date = self.blacklisted_date

    def __repr__(self):
        return "<Blacklist('%s','%s')>" % (self.user.username, self.target_user.username) 

class Message(object):
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

class Banner(object): 
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

class Welcome(object): 
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

class File(object): 
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

class Visitor(object):
    def __init__(self):
        self.total = 0
        self.today = 0
        self.date = datetime.datetime.fromtimestamp(time.time())

    def __repr__(self):
        return "<Visitor<'%d','%d'>" % (self.total, self.today)

# TODO: Table 정의에 Key Index 추가하기
metadata = MetaData()
users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', Unicode(40), unique=True),
    Column('password', Unicode(50)),
    Column('nickname', Unicode(40)),
    Column('email', Unicode(60), unique=True),
    Column('signature', Unicode(1024)),
    Column('self_introduction', Unicode(1024)),
    Column('default_language', Unicode(5)),  # ko_KR, en_US
    Column('campus', Unicode(15)),  # Null, Seoul, Daejeon
    Column('activated', Boolean),
    Column('widget', Integer),
    Column('layout', Integer),
    Column('join_time', DateTime),
    Column('last_login_time', DateTime),
    Column('last_logout_time', DateTime),
    Column('last_login_ip', Unicode(15)),
    Column('is_sysop', Boolean),
    mysql_engine='InnoDB'
)

bbs_managers_table = Table('bbs_managers', metadata,
    Column('id', Integer, primary_key=True),
    Column('board_id', Integer, ForeignKey('boards.id')),
    Column('manager_id', Integer, ForeignKey('users.id')),
    mysql_engine='InnoDB'
)

user_activation_table = Table('user_activation', metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('activation_code', Unicode(50), unique=True),
    Column('issued_date', DateTime),
    mysql_engine='InnoDB'
)

board_table = Table('boards', metadata,
    Column('id', Integer, primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('board_name', Unicode(30), unique=True),
    Column('board_description', Unicode(300)),
    Column('deleted', Boolean),
    Column('read_only', Boolean),
    Column('hide', Boolean),
    Column('order', Integer, nullable=True),
    mysql_engine='InnoDB'
)

category_table = Table('categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('category_name', Unicode(30), unique=True),
    mysql_engine='InnoDB'
)

board_heading_table = Table('board_headings', metadata,
    Column('id', Integer, primary_key=True),
    Column('board_id', Integer, ForeignKey('boards.id')),
    Column('heading', Unicode(10)),
    mysql_engine='InnoDB'
)

link_table = Table('links', metadata, 
    Column('id', Integer, primary_key=True),
    Column('link_name', Unicode(30), unique=True),
    Column('link_description', Unicode(300)),
    Column('link_url', Unicode(100)),
    Column('ishidden', Boolean),
    Column('deleted', Boolean),
    Column('order', Integer),
    mysql_engine='InnoDB'
)

articles_table = Table('articles', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', Unicode(200)),
    Column('board_id', Integer, ForeignKey('boards.id')),
    Column('heading_id', Integer, ForeignKey('board_headings.id'), nullable=True), # TODO: nullable=True 는 어디까지나 임시방편이므로 어서 지운다.
    Column('content', UnicodeText),
    Column('author_id', Integer, ForeignKey('users.id')),
    Column('author_nickname', Unicode(40)),
    Column('author_ip', Unicode(15)),
    Column('date', DateTime),
    Column('hit', Integer),
    Column('positive_vote', Integer),
    Column('negative_vote', Integer),
    Column('deleted', Boolean),
    Column('root_id', Integer, ForeignKey('articles.id'), nullable=True),
    Column('parent_id', Integer, ForeignKey('articles.id'), nullable=True),
    Column('reply_count', Integer, nullable=False),
    Column('is_searchable', Boolean, nullable=False),
    Column('last_modified_date', DateTime),
    # XXX 2010.05.17.
    # destroyed 필드는 nullable = False 로 해야 할 것 같은데
    # 이렇게 하면 테스트 코드가 깨진다.
    # SQLite 자체의 문제인 것 같으나 아직은 확신이 없다.
    Column('destroyed', Boolean),
    # XXX 여기까지.
    # XXX 2010.06.17.
    # 새로운 Field 를 추가한다. last_reply_date 마지막으로 reply 가 달린 / 수정된 시각.
    Column('last_reply_date', DateTime),
    # XXX 2010.06.18.
    # 새로운 Field 를 추가한다. last_reply_id 마지막으로 달린 reply 의 글 번호.
    # TODO: 사실 이 자리에는 id 가 아니라 article 객체가 와야 한다.
    Column('last_reply_id', Integer),
    mysql_engine='InnoDB'
)

article_vote_table = Table('article_vote_status', metadata,
    Column('id', Integer, primary_key=True),
    Column('board_id', Integer, ForeignKey('boards.id'), nullable=False),
    Column('article_id', Integer, ForeignKey('articles.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    mysql_engine='InnoDB'
)

class MyPickleType(PickleType):
    impl = MSLongBlob

read_status_table = Table('read_status', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('read_status_data', MyPickleType),
    mysql_engine='InnoDB'
)

blacklist_table = Table('blacklists' , metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('blacklisted_user_id', Integer, ForeignKey('users.id')),
    Column('blacklisted_date', DateTime),
    Column('last_modified_date', DateTime),
    Column('block_article', Boolean),
    Column('block_message', Boolean),
    mysql_engine='InnoDB'
)

message_table = Table('messages', metadata,
    Column('id', Integer, primary_key=True),
    Column('from_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('from_ip', Unicode(15)),
    Column('to_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('sent_time', DateTime),
    Column('message', Unicode(1000)),
    Column('received_deleted', Boolean),
    Column('sent_deleted', Boolean),
    Column('read_status', Unicode(1)),
    mysql_engine='InnoDB'
)

banner_table = Table('banners' , metadata,
    Column('id', Integer, primary_key=True),
    Column('content', UnicodeText),
    Column('issued_date', DateTime),
    Column('due_date', DateTime),
    Column('valid', Boolean),
    Column('weight', Integer),
    mysql_engine='InnoDB'
)

welcome_table = Table('welcomes' , metadata,
    Column('id', Integer, primary_key=True),
    Column('content', UnicodeText),
    Column('issued_date', DateTime),
    Column('due_date', DateTime),
    Column('valid', Boolean),
    Column('weight', Integer),
    mysql_engine='InnoDB'
)

file_table = Table('files', metadata,
    Column('id', Integer, primary_key=True),
    Column('filename', Unicode(200)),
    Column('saved_filename', Unicode(200)),
    Column('filepath', Text), 
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('board_id', Integer, ForeignKey('boards.id')),
    Column('article_id', Integer, ForeignKey('articles.id')),
    Column('deleted', Boolean),
    mysql_engine='InnoDB'
)

visitor_table = Table('visitors', metadata,
    Column('total', Integer, primary_key=True),
    Column('today', Integer),
    Column('date', DateTime),
    mysql_engine='InnoDB'
)

# TODO: 아래 mapper 들 좀 제대로 올바르게 정의하기
mapper(Category, category_table)

mapper(Visitor, visitor_table)

mapper(File, file_table, properties={
    'user':relation(User, backref='files', lazy=True),
    'board':relation(Board, backref=None, lazy=True),
    'article':relation(Article, backref=None, lazy=True),
})

mapper(Link, link_table)

mapper(Banner, banner_table)

mapper(Welcome, welcome_table)

mapper(User, users_table)

mapper(BBSManager, bbs_managers_table, properties={
    'board': relation(Board, backref='management', lazy=True),
    'manager': relation(User, backref='managing_board', lazy=True),
})

mapper(UserActivation, user_activation_table, properties={
    'user':relation(User, backref='activation', uselist=False)
})

mapper(Article, articles_table, properties={
    'author':relation(User, backref='articles', lazy=False),
    'board':relation(Board, backref='articles', lazy=False),
    'heading':relation(BoardHeading, backref='articles', lazy=False),
    'children':relation(Article,
        join_depth=3,
        primaryjoin=articles_table.c.parent_id==articles_table.c.id,
        backref=backref('parent', lazy=True,
            remote_side=[articles_table.c.id],
            primaryjoin=articles_table.c.parent_id==articles_table.c.id,
            )
        ),
    'descendants':relation(Article, lazy=True,
        primaryjoin=articles_table.c.root_id==articles_table.c.id,
        backref=backref('root',
            remote_side=[articles_table.c.id],
            primaryjoin=articles_table.c.root_id==articles_table.c.id,
            )
        )
})

mapper(ArticleVoteStatus, article_vote_table, properties={
    'article':relation(Article, backref='voted_users', lazy=True),
    'user':relation(User, backref='voted_articles', lazy=True),
    'board':relation(Board, backref=None, lazy=True),
})

mapper(ReadStatus, read_status_table, properties={
    'user': relation(User, backref='read_status'),
})

mapper(Board, board_table, properties={
    'category': relation(Category, backref='boards')
})

mapper(BoardHeading, board_heading_table, properties={
    'board': relation(Board, backref='headings', lazy=False),
})

mapper(Message, message_table, properties={
    'from_user': relation(User, primaryjoin=message_table.c.from_id==users_table.c.id,
                    backref=backref('send_messages', lazy=True, join_depth=1,
                                    primaryjoin=message_table.c.from_id==users_table.c.id,
                                    viewonly=False)
        ),
    'to_user': relation(User, primaryjoin=message_table.c.to_id==users_table.c.id,
                    backref=backref('received_messages', lazy=True, join_depth=1,
                                    primaryjoin=message_table.c.to_id==users_table.c.id,
                                    viewonly=False)
        ),
})

mapper(Blacklist, blacklist_table, properties={
    'user':relation(User, lazy=False, primaryjoin=blacklist_table.c.user_id==users_table.c.id,
                    backref=backref('blacklist', lazy=True, join_depth=1,
                                    primaryjoin=blacklist_table.c.user_id==users_table.c.id,
                                    viewonly=True)),
    'target_user':relation(User, lazy=False, primaryjoin=blacklist_table.c.blacklisted_user_id==users_table.c.id,
                    backref=backref('blacklisted', lazy=True, join_depth=1,
                                    primaryjoin=blacklist_table.c.blacklisted_user_id==users_table.c.id,
                                    viewonly=True)),
})

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
                             'assert_unicode': None}
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
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)

def init_test_database():
    '''
    TEST 를 위한 Database 를 메모리 상에 만든다. 물론 Session 도.
    '''
    global engine, Session
    engine = create_engine('sqlite://', convert_unicode=True, encoding='utf-8', echo=False)
    Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)
    metadata.create_all(engine)

def clear_test_database():
    """테스트 이후의 흔적을 지운다."""
    pass
