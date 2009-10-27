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
    if type(string) == str:
        return unicode(string, 'UTF-8', 'replace')
    else:
        return unicode(string)

SALT_SET = string.lowercase + string.uppercase + string.digits + './'

class User(object):
    def __init__(self, username, password, nickname, email, signature,
                 self_introduction, default_language):
        self.username = smart_unicode(username)
        self.set_password(password)
        self.nickname = smart_unicode(nickname)
        self.email = smart_unicode(email)
        self.signature = smart_unicode(signature)
        self.self_introduction = smart_unicode(self_introduction)
        self.default_language = smart_unicode(default_language)
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
        salt = ''.join(random.sample(SALT_SET, 2))
        return self.encrypt_password(raw_password, salt)

    def set_password(self, password):
        self.password = smart_unicode(self.crypt_password(password))

    def compare_password(self, password):
        hash_from_user = self.encrypt_password(password, self.password)
        hash_from_db = self.password
        hash_from_user = smart_unicode(hash_from_user.strip())
        hash_from_db = smart_unicode(hash_from_db.strip())
        return hash_from_user == hash_from_db

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.username, self.nickname)

class UserActivation(object):
    def __init__(self, user, activation_code):
        self.user = user
        self.activation_code = smart_unicode(activation_code)
        self.issued_date = datetime.datetime.fromtimestamp(time.time())

    def __repr__(self):
        return "<UserActivation('%s', '%s')>" % (self.user.username, self.activation_code)

class Board(object):
    def __init__(self, board_name, board_description):
        self.board_name = smart_unicode(board_name)
        self.board_description = smart_unicode(board_description)
        self.deleted = False
        self.read_only = False

    def __repr__(self):
        return "<Board('%s', '%s')>" % (self.board_name, self.board_description)

class Article(object):
    def __init__(self, board, title, content, author, author_ip, parent):
        self.board = board
        self.title = smart_unicode(title)
        self.content = smart_unicode(content)
        self.author = author
        self.author_ip = smart_unicode(author_ip)
        self.deleted = False
        self.date = datetime.datetime.fromtimestamp(time.time())
        self.hit = 0
        self.vote = 0
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

    def __repr__(self):
        return "<Article('%s', '%s', %s)>" % (self.title, self.author.username, str(self.date))

class ArticleVoteStatus(object):
    def __init__(self, user, board, article):
        self.user = user
        self.board = board
        self.article = article

class ReadStatus(object):
    def __init__(self, user, read_status_data):
        self.user = user
        self.read_status_data = read_status_data

    def __repr__(self):
        return "<ReadStatus('%s', '%s')>" % (self.user.username, self.read_status_data)

class Blacklist(object):
    def __init__(self, user, target_user, block_article, block_message):
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
        self.content = smart_unicode(content)
        self.valid = True
        self.weight = weight
        self.issued_date = datetime.datetime.fromtimestamp(time.time()) 
 	self.due_date = due_date 

    def __repr__(self):
        return "<Banner('%s','%s')>" % (self.content, self.valid)

class Welcome(object): 
    def __init__(self, content, weight, due_date): 
        self.content = smart_unicode(content)
        self.valid = True
        self.weight = weight
        self.issued_date = datetime.datetime.fromtimestamp(time.time()) 
 	self.due_date = due_date 

    def __repr__(self):
        return "<Welcome('%s','%s')>" % (self.content, self.valid)

class File(object): 
    def __init__(self, filename, saved_filename, filepath, user, board, article): 
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

user_activation_table = Table('user_activation', metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('activation_code', Unicode(50), unique=True),
    Column('issued_date', DateTime),
    mysql_engine='InnoDB'
)

board_table = Table('boards', metadata,
    Column('id', Integer, primary_key=True),
    Column('board_name', Unicode(30), unique=True),
    Column('board_description', Unicode(300)),
    Column('deleted', Boolean),
    Column('read_only', Boolean),
    mysql_engine='InnoDB'
)

articles_table = Table('articles', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', Unicode(200)),
    Column('board_id', Integer, ForeignKey('boards.id')),
    Column('content', UnicodeText),
    Column('author_id', Integer, ForeignKey('users.id')),
    Column('author_ip', Unicode(15)),
    Column('date', DateTime),
    Column('hit', Integer),
    Column('vote', Integer),
    Column('deleted', Boolean),
    Column('root_id', Integer, ForeignKey('articles.id'), nullable=True),
    Column('parent_id', Integer, ForeignKey('articles.id'), nullable=True),
    Column('reply_count', Integer, nullable=False),
    Column('is_searchable', Boolean, nullable=False),
    Column('last_modified_date', DateTime),
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


mapper(Visitor, visitor_table)

mapper(File, file_table, properties={
    'user':relation(User, backref='files', lazy=True),
    'board':relation(Board, backref=None, lazy=True),
    'article':relation(Article, backref=None, lazy=True),
})

mapper(Banner, banner_table)

mapper(Welcome, welcome_table)

mapper(User, users_table)

mapper(UserActivation, user_activation_table, properties={
    'user':relation(User, backref='activation', uselist=False)
})

mapper(Article, articles_table, properties={
    'author':relation(User, backref='articles', lazy=False),
    'board':relation(Board, backref='articles', lazy=False),
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

mapper(Board, board_table)

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


import settings
CONNECTION_STRING = settings.DB_CONNECTION_STRING
#TEST_DATABASE_FILENAME = 'test.db'
#CONNECTION_STRING = 'sqlite:///%s' % TEST_DATABASE_FILENAME

engine = None
pool = None

def get_engine():
    '''Factory method to create database connection.'''
    global engine
    global pool
    if not engine:
        from sqlalchemy import create_engine
        if CONNECTION_STRING.startswith('mysql'):
            engine = create_engine(CONNECTION_STRING, encoding='utf-8',
                                convert_unicode=True, assert_unicode=False,
                                pool_size=30, max_overflow=10, pool_recycle=5, 
                                echo=False, echo_pool=False)  
            # (pipoket) Note: To see what`s happing to the pool, turn on echo_pool above.
        else:
            engine = create_engine(CONNECTION_STRING, encoding='utf-8',
                                convert_unicode=True, assert_unicode=None)
    pool = engine.pool
    return engine

Session = None

def init_database():
    global Session
    get_engine()
    metadata.create_all(engine)
    # TODO: 나중에 SQLAlchemy 0.5 로 갈 때는
    # transactional=True 대신 autocommit=False 로 한다.
    Session = sessionmaker(bind=engine, autoflush=True, transactional=True)

def init_test_database():
    """Test database must reset the database."""
    global engine, Session, namespace
    # 데이터베이스를 억지로 새로 만든다.
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://', convert_unicode=True, encoding='utf-8', echo=False)
    # TODO: 나중에 SQLAlchemy 0.5 로 갈 때는
    # transactional=True 대신 autocommit=False 로 한다.
    Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
    metadata.create_all(engine)

    # 네임스페이스 객체를 새로 만든다. (억지로)
    import arara
    arara.namespace = None
    arara.get_namespace()

def clear_test_database():
    """테스트 이후의 흔적을 지운다."""
    pass
