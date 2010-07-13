#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import time

from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara_thrift.ttypes import *
from etc.arara_settings import BOT_ACCOUNT_USERNAME, BOT_ACCOUNT_PASSWORD, BOT_SERVICE_SETTING

class BotManager(object):
    '''
    ARA BOT Service 관련 클래스
    '''
    def __init__(self, engine):
        self.engine = engine

        # BOT 설정이 켜져있지 않으면 종료
        from etc.arara_settings import BOT_ENABLED, BOT_SERVICE_LIST
        if not BOT_ENABLED:
            return

        # BOT_SERVICE_LIST에 있는 BOT들을 검사 후 해당 BOT의 Instance를 생성
        if 'weather' in BOT_SERVICE_LIST:
            self.weather_bot = WeatherBot(engine, self)

    def _init_board(self, board_name):
        '''
        BOT에게 필요한 Board를 생성한다.

        @rtype: Bool
        @return:
            1. 성공적으로 추가했을 경우: True
            2. 실패했을 경우: False
        '''
        try:
            board_list = self.engine.board_manager.get_board_list() 
            if not filter(lambda x:x.board_name == board_name, board_list):
                self.engine.board_manager._add_bot_board(board_name)
            return True
        # TODO: 상황에 따라 다른 대처가 필요하다.
        except:
            return False

    def refresh_weather_info(self, session_key):
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('You are not SYSOP')
        if not self.weather_bot:
            raise InvalidOperation('Weather Bot is not enabled!')
        self.weather_bot.write_weather_article()

    def get_weather_info(self, session_key):
        if not self.weather_bot:
            raise InvalidOperation('Weather Bot is not enabled!')
        return self.weather_bot.recent_weather_info(session_key)

class WeatherBot(object):
    def __init__(self, engine, manager):
        import thread

        # 설정을 받아옴
        self.engine = engine
        self.manager = manager
        self.board_name = BOT_SERVICE_SETTING['weather_board_name']
        self.refresh_period = BOT_SERVICE_SETTING['weather_refresh_period']

        # Check 1. Board Initialization
        while not (self.manager._init_board(self.board_name)):
            pass

        # Check 2. Manager Status Check
        while not (self.check_manager_status()):
            pass

        # Check를 모두 통과하면 이제 새로운 스레드를 시작한다
        thread.start_new_thread(self.process, tuple())

    def check_manager_status(self):
        '''
        Weather Bot에 필요한 각 Manager들이 제대로 작동하고 있는지 검사한다.

        @rtype: Bool
        @return:
            1. 잘 작동하고 있을 경우: True
            2. 잘 작동하고 있지 않을 경우: False
        '''
        try:
            # Login Manager(혹은 연동되는 Manager)가 작동하고 있지 않거나, BOT_ACCOUNT_USERNAME, BOT_ACCOUNTPASSWORD의 설정이 잘못되었을 경우 문제가 발생한다
            session_key = self.engine.login_manager.login(BOT_ACCOUNT_USERNAME, BOT_ACCOUNT_PASSWORD, u'127.0.0.1')
        # TODO: 상황에 따라 다른 대처가 필요하다
        except:
            return False

        try:
            # Article Manager(혹은 연동되는 Manager)가 작동하고 있지 않거나, Board name 설정이 잘못된 경우
            # weather용 board에 대한 article_list를 Test용 함수로 사용한다.
            self.engine.article_manager.article_list(session_key, self.board_name, u'')
            self.engine.login_manager.logout(session_key)
            return True
        # TODO: 상황에 따라 다른 대처가 필요하다
        except:
            self.engine.login_manager.logout(session_key)
            return False

    def process(self):
        '''
        일정 주기마다 한 번씩 새 글을 작성하는 함수를 호출함
        
        @rtype: void
        @return: void
        '''
        while self.write_weather_article():
            time.sleep(self.refresh_period)
    
    def write_weather_article(self):
        '''
        날씨 정보를 긁어와 WEATHER_BOARD_NAME 게시판에 새 글로 작성함
        WeatherBot.process에서 일정 주기로 호출하거나, SYSOP 페이지에서 호출한다

        @rtype: bool
        @return: 
            1. 성공 : True
            2. 실패 : False
        '''
        

        logger = logging.getLogger('weather_refresh_bot')
        logger.info("[WRBot] Weather Refresh Bot Started!")

        # 로그인 시도. 실패시 log를 남기고 종료
        try:
            session_key = self.engine.login_manager.login(BOT_ACCOUNT_USERNAME, BOT_ACCOUNT_PASSWORD, u'127.0.0.1')
        except:
            logger.exception('[WRBot] Check weather bot`s username and password')
            return False

        # 날씨 정보를 받아온다(from google)
        import urllib
        import xml.dom.minidom
        today_string = time.strftime("%Y-%m-%d (%a) %H:%M:%S", time.localtime())

        # Dom 객체 초기화
        dom_implementation = xml.dom.minidom.getDOMImplementation()
        new_document = dom_implementation.createDocument(None, "araraWeatherInfo", None)

        # 각 캠퍼스의 정보를 받아옴
        for campus_location in BOT_SERVICE_SETTING['weather_service_area']:
            xmlsession = urllib.urlopen('http://www.google.com/ig/api?weather=' + campus_location + '&;ie=utf-8&oe=utf-8&hl=en')
            weather_xml = xml.dom.minidom.parseString(xmlsession.read())
            new_document.documentElement.appendChild(weather_xml.documentElement)
            xmlsession.close()

        contents = new_document.documentElement.toprettyxml()
        # weather_board_name 게시판에 새 글로 작성. 실패시 log를 남기고 종료.
        try:
            article_dic = {'title': today_string, 'content': contents, 'heading': u''}
            self.engine.article_manager.write_article(session_key, self.board_name, WrittenArticle(**article_dic))

            # 성공적으로 글을 작성하였음. log를 남기고 종료
            logger.info('[WRBot] Successfully Refreshed weather information at %s',today_string)
            self.engine.login_manager.logout(session_key)
            return True
        except:
            logger.exception('[WRBot] Check weather board name')
            self.engine.login_manager.logout(session_key)
            return False

    def recent_weather_info(self, session_key):
        '''
        WEATHER_BOARD_NAME 게시판에서 가장 최신 글을 읽어와 Parsing한 후 WeatherInfo 객체로 만들어주는 함수.
        WeatherInfo는 다음과 같은 구성요소들로 이루어져 있다
        WeatherInfo {city, current_temperature, current_condition, current_icon_url, tomorrow_icon_url, day_after_tomorrow_icon_url} 

        @type  session_key: string
        @param session_key: User Key
        @rtype: WeatherInfo object
        @return:
            1. 성공 시 : WeatherInfo Object
            2. 실패 시 : InvalidOperation
        '''

        # Read member's campus data. If user doesn't set campus, then return empty campus
        if session_key == '':
            return WeatherInfo()
        member = self.engine.member_manager.get_info(unicode(session_key))
        member.campus = member.campus.lower()
        if member.campus == '':
            return WeatherInfo()
        
        # Parsing content by xml.dom.minidom.
        import xml.dom.minidom
        result = self.engine.article_manager.read_recent_article(session_key, self.board_name)
        weather_xml = xml.dom.minidom.parseString(result[0].content)
        weather_info_dict = {}

        weather_info = weather_xml.getElementsByTagName('weather')
        for element in weather_info:
            city_code = element.getElementsByTagName('forecast_information')[0].getElementsByTagName('city')[0].getAttribute('data')
            city_code = city_code.lower()

            # If this element is same with member's campus location : Fill the dict
            if city_code == member.campus:
                current_weather_node = element.getElementsByTagName('current_conditions')[0]
                tomorrow_weather_node = element.getElementsByTagName('forecast_conditions')[0]
                day_after_tomorrow_weather_node = element.getElementsByTagName('forecast_conditions')[1]

                weather_info_dict['city'] = city_code
                weather_info_dict['current_temperature'] = int(current_weather_node.getElementsByTagName('temp_c')[0].getAttribute('data'))
                weather_info_dict['current_condition'] = current_weather_node.getElementsByTagName('condition')[0].getAttribute('data')
                weather_info_dict['current_icon_url'] = current_weather_node.getElementsByTagName('icon')[0].getAttribute('data')
                weather_info_dict['tomorrow_icon_url'] = tomorrow_weather_node.getElementsByTagName('icon')[0].getAttribute('data')
                weather_info_dict['day_after_tomorrow_icon_url'] = day_after_tomorrow_weather_node.getElementsByTagName('icon')[0].getAttribute('data')
                break

        if len(weather_info_dict) != 6:
            return WeatherInfo()
        else:
            return WeatherInfo(**weather_info_dict)




