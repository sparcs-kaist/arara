#-*- coding: utf-8 -*-
import unittest
import etc.arara_settings
import logging
import arara.model, arara.arara_engine
import smtplib
import time

import libs
from arara_thrift import ttypes

# Mockup Object for smtplib.SMTP()
class SMTPMockup(object):
    mail_list = []

    def __init__(self, debug = False):
        self.debug = debug

    def connect(self, host="localhost", port=25):
        if self.debug:
            print "CONNECT", host, port

    def sendmail(self, from_addr, to_addrs, msg):
        self.mail_list.append((from_addr, to_addrs, msg))
        if self.debug:
            print "SEND", from_addr, to_addrs, msg

    def quit(self):
        if self.debug:
            print "QUIT"

    @classmethod
    def print_mail(cls):
        for from_addr, to_addrs, msg in cls.mail_list:
            print "From:", from_addr
            print "To:", to_addrs
            print "Msg:"
            print msg
            print "======================================"

# Common Test Sets for all tests
class AraraTestBase(unittest.TestCase):
    def setUp(self, use_bot = False, mock_mail = True):
        self.use_bot = use_bot
        self.mock_mail = mock_mail

        # Overwrite Bot-related configuration
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = use_bot

        # Overwrite Mail-Transferring Libraries
        if mock_mail:
            self.org_SMTP = smtplib.SMTP
            smtplib.SMTP = SMTPMockup

        # Memcache Prefix Change to prevent collision
        if etc.arara_settings.USE_MEMCACHED:
            self.org_MEMCACHED_PREFIX = etc.arara_settings.MEMCACHED_PREFIX
            etc.arara_settings.MEMCACHED_PREFIX = str(int(time.time()) % 10000)

        # Set Logger
        logging.basicConfig(level=logging.ERROR)

        # Initialize Database
        arara.model.init_test_database()
        self.engine = arara.arara_engine.ARAraEngine()

    def tearDown(self):
        self.engine.shutdown()

        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED

        if self.mock_mail:
            smtplib.SMTP = SMTPMockup
            # If you want to test SMTPMockup object, uncomment next line
            # SMTPMockup.print_mail()


        # Memcache Prefix Rollback
        if etc.arara_settings.USE_MEMCACHED:
            etc.arara_settings.MEMCACHED_PREFIX = self.org_MEMCACHED_PREFIX

    @classmethod
    def get_user_reg_dic(cls, username, default_user_reg_dic=None):
        '''
        사용자 등록에 사용되는 User Registration Dictionary 를 생성한다.

        @type  username: str
        @param username: 등록하고자 하는 사용자의 username
        @type  default_user_reg_dic: dict
        @param default_user_reg_dic: 사용자 등록 시 지정할 값들
        @rtype: dict
        @return: 해당 사용자에 대한 User Registration Dictionary
        '''
        default_user_reg_dic = default_user_reg_dic or {}

        # Default User Registration Dictionary
        username = libs.smart_unicode(username)
        user_reg_dic = {
            'username': username,
            'password': username,
            'nickname': username,
            'email': username + u'@kaist.ac.kr',
            'signature': username,
            'self_introduction': username,
            'default_language': u'english',
            'campus': u'Daejeon'
        }
        # 파라메터로 지정된 값들은 덮어쓴다.
        for key in default_user_reg_dic:
            user_reg_dic[key] = default_user_reg_dic[key]

        return user_reg_dic

    def register_user(self, username, confirm=True, default_user_reg_dic=None):
        '''
        사용자를 등록한다. 별도의 에러 처리가 없으니 사용시 주의.
        또한 MemberManager 구현에 의존적인 점도 주의.

        @type  username: str
        @param username: 등록하고자 하는 사용자의 username
        @type  confirm: bool
        @param confirm: 사용자를 activate 하는가의 여부 (기본값: True)
        @type  default_user_reg_dic: dict
        @param default_user_reg_dic: 사용자 등록 시 지정할 값들 (기본값: {})
        @rtype: str
        @return: 해당 사용자에 대한 registration key
        '''
        default_user_reg_dic = default_user_reg_dic or {}

        user_reg_dic = self.get_user_reg_dic(username, default_user_reg_dic)
        register_key = self.engine.member_manager.register_(
                ttypes.UserRegistration(**user_reg_dic))
        if confirm:
            self.engine.member_manager.confirm(username, register_key)

        return register_key

    def register_and_login(self, username, default_user_reg_dic=None,
            ip="127.0.0.1"):
        '''
        사용자를 등록하고, 바로 로그인한다.
        MemberManager, LoginManager 구현이 바르다는 것을 가정한다.

        @type  username: str
        @param username: 등록하고자 하는 사용자의 username
        @type  default_user_reg_dic: dict
        @param default_user_reg_dic: 사용자 등록 시 지정할 값들 (기본값: {})
        @rtype: str
        @return: 사용자 Login Session
        '''
        default_user_reg_dic = default_user_reg_dic or {}

        _ = self.register_user(username, True, default_user_reg_dic)
        password = default_user_reg_dic.get("password", username)

        return self.engine.login_manager.login(username, password, ip)
