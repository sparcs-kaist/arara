#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import time

from arara import arara_manager
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara_thrift.ttypes import *
from etc.arara_settings import BOT_ACCOUNT_USERNAME, BOT_ACCOUNT_PASSWORD, BOT_SERVICE_SETTING

class BotManager(arara_manager.ARAraManager):
    '''
    ARA BOT Service 관련 클래스
    '''
    def __init__(self, engine):
        '''
        @type  engine: ARAraEngine
        '''
        # TODO: BOT_ENABLED 를 ARAraEngine 의 생성자로 넣는 게 어떨까
        super(BotManager, self).__init__(engine)

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

        @type  board_name: string
        @param board_name: BOT 을 위해 필요한 board
        @rtype: Bool
        @return:
            1. 성공적으로 추가했을 경우: True
            2. 실패했을 경우: False
        '''
        # TODO: 차라리 Backend 에 board 의 존재 유무를 알려주는 함수를 만들자
        # TODO: T/F 를 리턴하는 함수일 필요가 있는가?
        try:
            board_list = self.engine.board_manager.get_board_list() 
            if not filter(lambda x:x.board_name == board_name, board_list):
                self.engine.board_manager._add_bot_board(board_name)
            return True
        # TODO: 상황에 따라 다른 대처가 필요하다.
        except:
            return False

    def refresh_weather_info(self, session_key):
        '''
        WeatherBot 에게 일부러 날씨 정보 갱신 명령을 내린다.

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        '''
        # TODO: sysop 이 아니라면 알아서 InvalidOperation 을 raise 해 주는 그런 게 있음 좋겠다
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('You are not SYSOP')
        if not self.weather_bot:
            raise InvalidOperation('Weather Bot is not enabled!')
        self.weather_bot.write_weather_article()

    def get_weather_info(self, session_key):
        '''
        WeatherBot 이 긁어온 날씨 정보를 참고로 날씨 정보를 얻어낸다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: ttypes.WeatherInfo
        @return: 주어진 사용자의 지역에 알맞은 Weather Info
        '''
        if not self.weather_bot:
            raise InvalidOperation('Weather Bot is not enabled!')
        return self.weather_bot.recent_weather_info(session_key)

    __public__ = [
            refresh_weather_info,
            get_weather_info]

class WeatherBot(object):
    def __init__(self, engine, manager):
        '''
        @type  engine: ARAraEngine
        @type  manager: BotManager
        '''
        import thread

        # 설정을 받아옴
        self.engine = engine
        self.manager = manager
        self.board_name = BOT_SERVICE_SETTING['weather_board_name']
        self.refresh_period = BOT_SERVICE_SETTING['weather_refresh_period']

        thread.start_new_thread(self.process, tuple())

    def check_manager_status(self):
        '''
        Weather Bot에 필요한 각 Manager들이 제대로 작동하고 있는지 검사한다.

        @rtype: Boolean
        @return:
            잘 작동되고 있을 때는 True, 그렇지 않을 때는 logger 에 로그를 남기고 False
        '''
        # Check 1. Board Initialization
        if not (self.manager._init_board(self.board_name)):
            return False

        try:
            # BOT_ACCOUNT_USERNAME, BOT_ACCOUNTPASSWORD의 설정이 잘못되었을 경우 문제가 발생한다
            session_key = self.engine.login_manager.login(BOT_ACCOUNT_USERNAME, BOT_ACCOUNT_PASSWORD, u'127.0.0.1')
        # TODO: 상황에 따라 다른 대처가 필요하다
        except:
            logger = logging.getLogger('weather_refresh_bot')
            logger.exception('Weather BOT cannot login with bot account')
            return False

        try:
            # Board name 설정이 잘못된 경우 문제가 발생한다
            # weather용 board에 대한 article_list를 Test용 함수로 사용한다.
            self.engine.article_manager.article_list(session_key, self.board_name, u'', 1, 1, True)
        except:
            logger = logging.getLogger('weather_refresh_bot')
            logger.exception('Weather BOT cannot get article list from weather board')
            return False

        try:
            self.engine.login_manager.logout(session_key)
        except:
            logger = logging.getLogger('weather_refresh_bot')
            logger.exception('Weather BOT cannot logout (...)')
            return False

        # 이상의 테스트를 모두 통과하면 문제없이 동작한다는 것.
        return True

    def process(self):
        '''
        일정 주기마다 한 번씩 새 글을 작성하는 함수를 호출함
        
        @rtype: void
        @return: void
        '''
        # Weather Bot 이 활동할 수 있는 상황이 될 때까지 기다린다
        while not self.check_manager_status():
            time.sleep(1)

        # TODO: 프로그램이 종료됨이 확실한 순간에는 스레드도 죽이도록 하자
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
        # TODO: Return 된 결과로 무엇을 할 수 있는가?
        
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
            xmlsession = urllib.urlopen('http://www.google.com/ig/api?weather=' + campus_location + '&;ie=utf-8&oe=utf-8&hl=ko')
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
        WeatherInfo {city, current_temperature, current_condition, current_icon_url, tomorrow_icon_url, tomorrow_temperature_high, tomorrow_temperature_low, day_after_tomorrow_icon_url, day_after_tomorrow_temperature_high, day_after_tomorrow_temperature_low} 

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: ttypes.WeatherInfo
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

                weather_info_dict['city'] = city_code[0].upper() + city_code[1:].lower()
                weather_info_dict['current_temperature'] = int(current_weather_node.getElementsByTagName('temp_c')[0].getAttribute('data'))
                weather_info_dict['current_condition'] = current_weather_node.getElementsByTagName('condition')[0].getAttribute('data')
                weather_info_dict['current_icon_url'] = current_weather_node.getElementsByTagName('icon')[0].getAttribute('data')
                weather_info_dict['tomorrow_icon_url'] = tomorrow_weather_node.getElementsByTagName('icon')[0].getAttribute('data')
                weather_info_dict['tomorrow_temperature_high'] = int(tomorrow_weather_node.getElementsByTagName('high')[0].getAttribute('data'))
                weather_info_dict['tomorrow_temperature_low'] = int(tomorrow_weather_node.getElementsByTagName('low')[0].getAttribute('data'))
                weather_info_dict['day_after_tomorrow_icon_url'] = day_after_tomorrow_weather_node.getElementsByTagName('icon')[0].getAttribute('data')
                weather_info_dict['day_after_tomorrow_temperature_high'] = int(day_after_tomorrow_weather_node.getElementsByTagName('high')[0].getAttribute('data'))
                weather_info_dict['day_after_tomorrow_temperature_low'] = int(day_after_tomorrow_weather_node.getElementsByTagName('low')[0].getAttribute('data'))
                break

        if len(weather_info_dict) != 10:
            return WeatherInfo()
        else:
            return WeatherInfo(**weather_info_dict)

