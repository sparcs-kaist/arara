import unittest
import etc.arara_settings
import logging
import arara.model, arara.arara_engine
import smtplib

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
    def setUp(self, use_bot = False, use_database = True, mock_mail = True):
        self.use_bot = use_bot
        self.use_database = use_database
        self.mock_mail = mock_mail

        # Overwrite Bot-related configuration
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = use_bot

        # Overwrite Mail-Transferring Libraries
        if mock_mail:
            self.org_SMTP = smtplib.SMTP
            smtplib.SMTP = SMTPMockup

        # Set Logger
        logging.basicConfig(level=logging.ERROR)

        # Initialize Database
        if use_database:
            arara.model.init_test_database()
            self.engine = arara.arara_engine.ARAraEngine()
        else:
            self.engine = None

    def tearDown(self):
        if self.use_database:
            self.engine.shutdown()
            arara.model.clear_test_database()

        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED

        if self.mock_mail:
            smtplib.SMTP = SMTPMockup
            # If you want to test SMTPMockup object, uncomment next line
            # SMTPMockup.print_mail()
