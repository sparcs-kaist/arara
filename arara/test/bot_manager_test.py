#-*- coding: utf-8 -*-
import unittest
import time
import os
import sys
import logging
import xml.dom.minidom
import thread
thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara_thrift.ttypes import *
import arara.model
from arara import arara_engine

import etc.arara_settings
from etc.arara_settings import BOT_SERVICE_SETTING, BOT_SERVICE_LIST

def stub_toprettyxml(url):
    return u'melong. this is xml'

def stub_strftime(formatstring, target):
    return u'melong. this is time'

def stub_start_new_thread(function, argument):
    pass

class BotManagerTest(unittest.TestCase):
    def setUp(self):
        # Before Initialization Engines, BOTs object should be Mock object
        ## This is for Weather Bot
        self.org_toprettyxml = xml.dom.minidom.Element.toprettyxml
        xml.dom.minidom.Element.toprettyxml = stub_toprettyxml
        self.org_strftime = time.strftime
        time.strftime = stub_strftime
        self.org_start_new_thread = thread.start_new_thread
        thread.start_new_thread = stub_start_new_thread

        # Common preparation for all tests ( Except etc.arara_settings.BOT_ENABLED = False )
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = True

        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        self.engine = arara_engine.ARAraEngine()

        self.session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'123.123.123.123.')

    def testInit(self):
        # 각각의 Bot의 Instance들을 제대로 생성했는지 검사
        if not('weather' in BOT_SERVICE_LIST and self.engine.bot_manager.weather_bot):
            self.fail('Weather bot is in service list but has not initialized')

    def testWeatherBot(self):
        # Weather Bot을 테스트
        self.engine.bot_manager.weather_bot.write_weather_article()

        recent_article = self.engine.article_manager.read_recent_article(self.session_key_sysop, BOT_SERVICE_SETTING['weather_board_name'])
        self.assertEqual(u'melong. this is time', recent_article[0].title)
        self.assertEqual(u'melong. this is xml', recent_article[0].content)

    def tearDown(self):
        # Restore Stub Code
        xml.dom.minidom.Element.toprettyxml = self.org_toprettyxml
        time.strftime = self.org_strftime
        thread.start_new_thread = self.org_start_new_thread
        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED
def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BotManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
