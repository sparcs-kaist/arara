#!/usr/bin/python
# -*- coding: utf-8 -*-

class Not_LoggedIn(Exception):
    pass

class NoticeManager(object):
    '''
    배너 및 환영 페이지 처리 관련 클래스
    '''

    def __init__(self, login_manager):
        self.banner = {}
        self.welcome = {}
        self.login_manager = login_manager

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
        try:
            return True, self.banner['1']
        except IndexError:
            return False, 'NO_BANNER'


    def get_welcome(self):
        '''
        환영 페이지를 가져오는 함수

        >>> notice.get_welcome()
        '스팍스에서 2009학년도 신입회원을 모집합니다. ...'

        @rtype: boolean, string
        @return:
            1. 환영 페이지가 있을 때: True, 환영 페이지(text)
            2. 환영 페이지가 없을 때: False, 'NO_WELCOME'
        '''
        try:
            return True, self.welcome['1']
        except IndexError:
            return False, 'NO_WELCOME'



    def list_welcome(self, session_key):
        '''
        관리자용 환영 페이지 목록을 가져오는 함수

        >>> notice.list_welcome(SYSOP_session_key)
        [{'welcome_no': 32, 'welcome_article': '신입회원을 모집합니다'}, {'welcome_no':33, 'welcome_article': '......'}, ....]

        @rtype: list
        @return:
            1. 환영 페이지가 있을 때: True, 환영 페이지들의 목록(text)
            2. 환영 페이지가 없을 때: 
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        

        try:
            if not self.login_manager.is_logged_in(session_key)[0]:
                raise NotLoggedIn()
        except NotLoggedIn:
            return False, 'NOT_SYSOP'
        
        '''DB에서 welcome 관련 해서 데이터 받아오는 부분 추가'''
        welcome = {}

        try:
            return True, self.welcome
        except IndexError:
            return False, 'NO_WELCOME'

        
    
    def list_banner(self, session_key):
        '''
        관리자용 배너 페이지 목록을 가져오는 함수

        >>> notice.list_welcome(SYSOP_session_key)
        True, [{'banner_no': 2, 'banner_article': '<html>....'}, {'banner_no': 3, 'banner_article': '<html>....'}, ....]
        >>> notice.list_welcome(user_session_key)
        False, ['NOT_SYSOP']

        @rtype: list
        @return:
            1. 배너 페이지 목록 읽기에 성공하였을 때: True, 배너 페이지들의 목록(text)
            2. 배너 페이지 목록 읽기에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        

        try:
            if not self.login_manager.is_logged_in(session_key)[0]:
                raise NotLoggedIn()
        except NotLoggedIn:
            return False, 'NOT_SYSOP'
        
        '''DB에서 banner 관련 해서 데이터 받아오는 부분 추가'''
        banner = {}

        try:
            return True, self.banner
        except IndexError:
            return False, 'NO_BANNER'



    
    def add_banner(self, session_key, banner_dic):
        '''
        관리자용 배너 추가 함수

        >>> notice.add_banner(SYSOP_session_key, banner_dic)
        True, 'OK'
        >>> notice.add_banner(user_session_key, banner_dic)
        False, 'NOT_SYSOP'
        
        --banner_dic {banner_no, banner_article}

        @rtype: string
        @return:
            1. 배너 페이지 추가에 성공하였을 때: True, 'OK'
            2. 배너 페이지 추가에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        

        try:
            if not self.login_manager.is_logged_in(session_key)[0]:
                raise NotLoggedIn()
        except NotLoggedIn:
            return False, 'NOT_SYSOP'
        

        try:
            # DB에서 banner 관련 해서 데이터 받아오는 부분 추가
            banner = {}
            banner[banner_dic['banner_no']] =  banner_dic['banner_article']
            return True, 'OK' 
        except DBError:
            return False, 'DATABASE_ERROR'
    

    def add_welcome(self, session_key, welcome_dic):
        '''
        관리자용 환영 페이지 추가 함수

        >>> notice.add_banner(SYSOP_session_key, banner_dic)
        True, 'OK'
        >>> notice.add_banner(user_session_key, banner_dic)
        False, 'NOT_SYSOP'
        
        --welcome_dic {welcome_no, welcome_article}

        @rtype: string
        @return:
            1. 환영 페이지 추가에 성공하였을 때: True, 'OK'
            2. 환영 페이지 추가에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 양식에 맞지 않을때 (80X23): False, 'TOO_BIG'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        

        try:
            if not self.login_manager.is_logged_in(session_key)[0]:
                raise NotLoggedIn()
        except NotLoggedIn:
            return False, 'NOT_SYSOP'
        

        try:
            '''DB에서 welcome 관련 해서 데이터 받아오는 부분 추가'''
            banner = {}
            banner[welcome_dic['welcome_no']] =  welcome_dic['welcome_article']
            return True, 'OK' 
        except DBError:
            return False, 'DATABASE_ERROR'
    



    
    def remove_banner(self, session_key, banner_no):
        '''
        관리자용 배너 제거 함수

        >>> notice.remove_banner(SYSOP_session_key, 33)
        True, 'OK'
        >>> notice.remove_banner(user_session_key, 33)
        False, 'NOT_SYSOP'
        >>> notice.remove_banner(SYSOP_session_key, -1)
        False, 'NOT_EXIST'

        @rtype: string
        @return:
            1. 배너 제거에 성공하였을 때: True, 'OK'
            2. 배너 제거에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 존재하지 않는 배너번호일 때: False, 'NOT_EXIST'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        

        try:
            if not self.login_manager.is_logged_in(session_key)[0]:
                raise NotLoggedIn()
        except NotLoggedIn:
            return False, 'NOT_SYSOP'

        try:
            '''DB에서 welcome 관련 해서 데이터 받아오는 부분 추가'''
            banner = {}
            return True, 'OK' 
        except DBError:
            return False, 'DATABASE_ERROR'
    
    def remove_welcome(self, session_key, welcome_no):
        '''
        관리자용 환영 페이지 제거 함수

        >>> notice.remove_welcome(SYSOP_session_key, 33)
        True, 'OK'
        >>> notice.remove_welcome(user_session_key, 33)
        False, 'NOT_SYSOP'
        >>> notice.remove_welcome(SYSOP_session_key, -1)
        False, 'NOT_EXIST'

        @rtype: string
        @return:
            1. 환영 페이지 제거에 성공하였을 때: True, 'OK'
            2. 환영 페이지 제거에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 존재하지 않는 배너번호일 때: False, 'NOT_EXIST'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        
        
        try:
            if not self.login_manager.is_logged_in(session_key)[0]:
                raise NotLoggedIn()
        except NotLoggedIn:
            return False, 'NOT_SYSOP'
        

        try:
            '''DB에서 welcome 관련 해서 데이터 받아오는 부분 추가'''
            banner = [{}]
            #banner.append({welcome_dic['welcome_no'], welcome_dic['welcome_article']})
            return True, 'OK' 
        except DBError:
            return False, 'DATABASE_ERROR'
    

