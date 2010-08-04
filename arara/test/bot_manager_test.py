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
    def _get_user_reg_dic(self, id, campus):
        return {'username':id, 'password':id, 'nickname':id, 'email':id + u'@example.com',
                'signature':id, 'self_introduction':id, 'default_language':u'english', 'campus':campus}

    def _register_user(self, id, campus):
        # Register a user, log-in, and then return its session_key
        user_reg_dic = self._get_user_reg_dic(id, campus)
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(id, unicode(register_key))
        return self.engine.login_manager.login(id, id, u'143.248.234.140')

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
        self.session_key_mikkang = self._register_user(u'mikkang', u'seoul')

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

    def testRefreshWeatherInfo(self):
        # refresh_weather_info가 정보를 잘 갱신하는지 검사하는 테스트이다
        def new_stub_toprettyxml(url):
            return u'melong. this is self-refreshed xml'
        xml.dom.minidom.Element.toprettyxml = new_stub_toprettyxml

        # 시삽이 아닌데도 refresh를 시도할 경우 에러를 내놓아야 한다
        try:
            self.engine.bot_manager.refresh_weather_info(self.session_key_mikkang)
            self.fail()
        except:
            pass
        self.engine.bot_manager.refresh_weather_info(self.session_key_sysop)

        # Recent Article을 긁어왔을 때 새로 갱신된 글이어야 한다.
        recent_article = self.engine.article_manager.read_recent_article(self.session_key_sysop, BOT_SERVICE_SETTING['weather_board_name'])
        self.assertEqual(u'melong. this is time', recent_article[0].title)
        self.assertEqual(u'melong. this is self-refreshed xml', recent_article[0].content)

    def testGetWeatherInfo(self):
        # get_weather_info가 정보를 잘 받아오는지 검사하는 테스트이다.
        # Initial setting for test this function
        self.session_key_hodduc = self._register_user(u'hodduc', u'daejeon')
        self.session_key_sillo = self._register_user(u'sillo', u'')
        self.engine.bot_manager.refresh_weather_info(self.session_key_sysop)

        def stub_parseString(string):
            f = open(os.path.join(os.path.dirname(__file__), 'bot_manager_test_weather_info.xml'), 'r')
            ret = xml.dom.minidom.parse(f)
            f.close()
            return ret
        self.org_parseString = stub_parseString
        xml.dom.minidom.parseString = stub_parseString

        # Session Key가 비었을 때 빈 인스턴스를 잘 들고 오는가?
        result = self.engine.bot_manager.get_weather_info(u"")
        self.assertEqual(result.city, None)

        # User가 Campus 정보를 입력하지 않았을 때 빈 인스턴스를 잘 들고 오는가?
        result = self.engine.bot_manager.get_weather_info(self.session_key_sillo)
        self.assertEqual(result.city, None)

        # Seoul 캠퍼스에 사는 Mikkang 유저에 대한 날씨 정보를 잘 들고 오는가?
        result = self.engine.bot_manager.get_weather_info(self.session_key_mikkang)
        self.assertEqual(result.city, 'Seoul')
        self.assertEqual(result.current_temperature, 21)
        self.assertEqual(result.current_condition, u'Partly Cloudy')
        self.assertEqual(result.current_icon_url, u'/ig/images/weather/partly_cloudy.gif')
        self.assertEqual(result.tomorrow_icon_url, u'/ig/images/weather/chance_of_rain.gif')
        self.assertEqual(result.day_after_tomorrow_icon_url, u'/ig/images/weather/chance_of_storm.gif')
        self.assertEqual(result.tomorrow_temperature_high, 89)
        self.assertEqual(result.tomorrow_temperature_low, 68)
        self.assertEqual(result.day_after_tomorrow_temperature_high, 87)
        self.assertEqual(result.day_after_tomorrow_temperature_low, 71)

        # Daejeon 캠퍼스에 사는 Hodduc 유저에 대한 날씨 정보를 잘 들고 오는가?
        result = self.engine.bot_manager.get_weather_info(self.session_key_hodduc)
        self.assertEqual(result.city, 'Daejeon')
        self.assertEqual(result.current_temperature, 25)
        self.assertEqual(result.current_condition, u'Mostly Cloudy')
        self.assertEqual(result.current_icon_url, u'/ig/images/weather/mostly_cloudy.gif')
        self.assertEqual(result.tomorrow_icon_url, u'/ig/images/weather/chance_of_rain.gif')
        self.assertEqual(result.day_after_tomorrow_icon_url, u'/ig/images/weather/chance_of_rain.gif')
        self.assertEqual(result.tomorrow_temperature_high, 80)
        self.assertEqual(result.tomorrow_temperature_low, 68)
        self.assertEqual(result.day_after_tomorrow_temperature_high, 84)
        self.assertEqual(result.day_after_tomorrow_temperature_low, 66)


        # Restore Stub Code
        xml.dom.minidom.parseString = self.org_parseString

    def tearDown(self):
        self.engine.shutdown()
        # Restore Stub Code
        xml.dom.minidom.Element.toprettyxml = self.org_toprettyxml
        time.strftime = self.org_strftime
        thread.start_new_thread = self.org_start_new_thread
        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BotManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
