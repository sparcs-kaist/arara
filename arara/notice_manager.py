#!/usr/bin/python
# -*- coding: utf-8 -*-

from arara.util import require_login, is_keys_in_dict, filter_dict
from arara import model
from sqlalchemy.exceptions import InvalidRequestError
import random

NOTICE_PUBLIC_KEYS = ('id', 'content', 'issued_date', 'due_date', 'valid', 'weight')
NOTICE_QUERY_WHITELIST = ('id', 'content', 'issued_date', 'due_date', 'valid', 'weight')
NOTICE_PUBLIC_WHITELIST= ('id', 'content', 'issued_date', 'due_date', 'valid', 'weight')
NOTICE_ADD_WHITELIST = ('content','due_date','weight')

class NoticeManager(object):
    '''
    배너 및 환영 페이지 처리 관련 클래스
    '''

    def __init__(self):
        self.banner_list = []
        self.welcome_list = []

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _set_member_manager(self, member_manager):
        self.member_manager = member_manager

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(filtered_dict)
        return return_list

    
    def get_banner(self):
        '''
        배너를 가져오는 함수

        >>> notice.get_banner()
        '<html> .... '

        @rtype: boolean, string
        @return:
            1. 배너가 있을 때: True, 랜덤하게 선택된 배너(html)
            2. 배너가 없을 때: False, 'NO_BANNER'
        '''
        session = model.Session()
        available_banner = session.query(model.Banner).filter_by(valid=True).all()
        available_banner_dict_list = self._get_dict_list(available_banner, NOTICE_PUBLIC_KEYS)
        if available_banner_dict_list:
            weight_banner = []
            for index in range(len(available_banner_dict_list)):
                for weight in range(available_banner_dict_list[index]['weight']):
                    weight_banner.append(index)
            n = random.choice(weight_banner)
            return True, available_banner_dict_list[n]['content']
        else:
            return False, 'NO_BANNER'


    def get_welcome(self):
        '''
        welcome 가져오는 함수

        >>> notice.get_welcome()
        '<html> .... '

        @rtype: boolean, string
        @return:
            1. welcome 있을 때: True, 랜덤하게 선택된 welcome(html)
            2. welcome 없을 때: False, 'NO_WELCOME'
        '''
        session = model.Session()
        available_welcome= session.query(model.Welcome).filter_by(valid=True).all()
        available_welcome_dict_list = self._get_dict_list(available_welcome, NOTICE_PUBLIC_KEYS)
        if available_welcome_dict_list:
            weight_welcome = []
            for index in range(len(available_welcome_dict_list)):
                for weight in range(available_welcome_dict_list[index]['weight']):
                    weight_welcome.append(index)
            n = random.choice(weight_welcome)
            return True, available_welcome_dict_list[n]['content']
        else:
            return False, 'NO_WELCOME'


    @require_login
    def list_banner(self, session_key):
        '''
        관리자용 banner 페이지 목록을 가져오는 함수

        >>> notice.list_banner(SYSOP_session_key)
        [{'no': 32, 'content': '신입회원을 모집합니다','availability': 'True'}, {'no': 33', content': '환영합니다','availability': 'False'}

        @rtype: list
        @return:
            1. banner 페이지가 있을 때: True, banner 페이지들의 목록(text)
            2. banner 페이지가 없을 때: 
                1. banner가 없을때  : False, 'NO_BANNER'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
            3. 시삽이 아닐 때: False, 'NOT_SYSOP'
        '''
        if not self.member_manager.is_sysop(session_key):
            return False, 'NOT_SYSOP'

        session = model.Session()
        banner = session.query(model.Banner).all()
        banner_dict_list = self._get_dict_list(banner, NOTICE_PUBLIC_KEYS)

        if banner_dict_list:
            return True, banner_dict_list
        else:    
            return False, 'NO_BANNER'

    @require_login
    def list_welcome(self, session_key):
        '''
        관리자용 welcome 페이지 목록을 가져오는 함수

        >>> notice.list_welcome(SYSOP_session_key)
        [{'no': 32, 'content': '신입회원을 모집합니다','availability': 'True'}, {'no': 33', content': '환영합니다','availability': 'False'}

        @rtype: list
        @return:
            1. welcome 페이지가 있을 때: True, welcome 페이지들의 목록(text)
            2. welcome 페이지가 없을 때: 
                1. welcome 없을때   : False, 'NO_WELCOME'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
            3. 시삽이 아닐 때: False, 'NOT_SYSOP'
        '''
        
        if not self.member_manager.is_sysop(session_key):
            return False, 'NOT_SYSOP'
        session = model.Session()
        welcome= session.query(model.Welcome).all()
        welcome_dict_list = self._get_dict_list(welcome, NOTICE_PUBLIC_KEYS)

        if welcome_dict_list:
            return True, welcome_dict_list
        else:    
            return False, 'NO_WELCOME'
        

    @require_login    
    def add_banner(self, session_key, notice_reg_dic):
        '''
        관리자용 배너 추가 함수

        >>> notice_reg_dic = { 'content':'hahahah', 'due_date':'2008,7,14', 'weight':'1' }
        >>> notice.add_banner(SYSOP_session_key, notice_reg_dic)
        True, 'OK'
        >>> notice.add_banner(user_session_key, notice_reg_dic)
        False, 'NOT_SYSOP'
        
        @type  session_key: string
        @param session_key: User Key
        @type  notice_reg_dic: dictionary
        @param notice_reg_dic: Notice Dictionary
        @rtype: string
        @return:
            1. 배너 페이지 추가에 성공하였을 때: True, 'OK'
            2. 배너 페이지 추가에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        if not is_keys_in_dict(notice_reg_dic, NOTICE_ADD_WHITELIST):
            return False, 'WRONG_DICTIONARY'

        if not self.member_manager.is_sysop(session_key):
            return False, 'NOT_SYSOP'

        session = model.Session()
        try:
            # Register welcome to db
            banner= model.Banner(**notice_reg_dic)
            session.save(banner)
            session.commit()
            return True, 'OK' 
        except Exception, e:
            raise
            session.rollback()
            return False, e

    @require_login    
    def add_welcome(self, session_key, notice_reg_dic):
        '''
        관리자용 welcome 추가 함수

        >>> notice_reg_dic = { 'content':'hahahah', 'due_date':'2008,7,14', 'weight':'1' }
        >>> notice.add_welcome(SYSOP_session_key, notice_reg_dic)
        True, 'OK'
        >>> notice.add_welcome(user_session_key, notice_reg_dic)
        False, 'NOT_SYSOP'
        
        @type  session_key: string
        @param session_key: User Key
        @type  notice_reg_dic: dictionary
        @param notice_reg_dic: Notice Dictionary
        @rtype: string
        @return:
            1. welcome 페이지 추가에 성공하였을 때: True, 'OK'
            2. welcome 페이지 추가에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        if not is_keys_in_dict(notice_reg_dic, NOTICE_ADD_WHITELIST):
            return False, 'WRONG_DICTIONARY'

        if not self.member_manager.is_sysop(session_key):
            return False, 'NOT_SYSOP'

        session = model.Session()
        try:
            # Register welcome to db
            welcome= model.Welcome(**notice_reg_dic)
            session.save(welcome)
            session.commit()
            return True, 'OK' 
        except Exception, e:
            raise
            session.rollback()
            return False, e

    @require_login 
    def remove_banner(self, session_key, id):
        '''
        관리자용 배너 제거 함수

        >>> notice.remove_banner(SYSOP_session_key, 33)
        True, 'OK'
        >>> notice.remove_banner(user_session_key, 33)
        False, 'NOT_SYSOP'
        >>> notice.remove_banner(SYSOP_session_key, -1)
        False, 'NOT_EXIST_BANNER'

        @rtype: string
        @return:
            1. 배너 제거에 성공하였을 때: True, 'OK'
            2. 배너 제거에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 존재하지 않는 배너번호일 때: False, 'NOT_EXIST_BANNER'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        if not self.member_manager.is_sysop(session_key):
            return False, 'NOT_SYSOP'
        try:
            session = model.Session()
            invalid_banner= session.query(model.Banner).filter_by(id = id).one()
            if invalid_banner:
                invalid_banner.valid = 'False'
                return True, 'OK' 
            else:
                return False, 'NOT_EXIST_WELCOME'
        except:
            raise
            return False, 'DATABASE_ERROR'
    
    @require_login 
    def remove_welcome(self, session_key, id):
        '''
        관리자용 welcome 제거 함수

        >>> notice.remove_welcome(SYSOP_session_key, 33)
        True, 'OK'
        >>> notice.remove_welcome(user_session_key, 33)
        False, 'NOT_SYSOP'
        >>> notice.remove_welcome(SYSOP_session_key, -1)
        False, 'NOT_EXIST_WELCOME'

        @rtype: string
        @return:
            1. welcome 제거에 성공하였을 때: True, 'OK'
            2. welcome 제거에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 존재하지 않는 welcome번호일 때: False, 'NOT_EXIST_WELCOME'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        if not self.member_manager.is_sysop(session_key):
            return False, 'NOT_SYSOP'
        try:
            session = model.Session()
            invalid_welcome= session.query(model.Welcome).filter_by(id = id).one()
            if invalid_welcome:
                invalid_welcome.valid = 'False'
                return True, 'OK' 
            else:
                return False, 'NOT_EXIST_WELCOME'
        except:
            raise
            return False, 'DATABASE_ERROR'

# vim: set et ts=8 sw=4 sts=4
