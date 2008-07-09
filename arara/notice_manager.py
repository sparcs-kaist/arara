#!/usr/bin/python
# -*- coding: utf-8 -*-

from arara.util import require_login

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
        available_banner = filter(lambda x: x['availability'] == 'True', self.banner_list)
        if available_banner:
            return True, available_banner[-1]['content']
            #나중에는 랜덤하게 토해내는 것으로 바꿀것임
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
        available_welcome = filter(lambda x: x['availability'] == 'True', self.welcome_list)
        if available_welcome:
            return True, available_welcome[-1]['content']
            #나중에는 랜덤하게 토해내는 것으로 바꿀것임
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
        
        '''DB에서 banner 관련 해서 데이터 받아오는 부분 추가'''

        if self.banner_list:
            return True, self.banner_list
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
        
        '''DB에서 welcome 관련 해서 데이터 받아오는 부분 추가'''

        if self.welcome_list:
            return True, self.welcome_list
        else:    
            return False, 'NO_WELCOME'
        

    @require_login    
    def add_banner(self, session_key, content):
        '''
        관리자용 배너 추가 함수

        >>> notice.add_banner(SYSOP_session_key, content)
        True, 'OK'
        >>> notice.add_banner(user_session_key, content)
        False, 'NOT_SYSOP'
        
        @type  session_key: string
        @param session_key: User Key
        @type  content: string 
        @param content: Banner Content(html tag)
        @rtype: string
        @return:
            1. 배너 페이지 추가에 성공하였을 때: True, 'OK'
            2. 배너 페이지 추가에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        if not self.member_manager.is_sysop(session_key):
            return False, 'NOT_SYSOP'
        try:
            # DB에서 banner 관련 해서 데이터 받아오는 부분 추가
            banner_dict = {'no': len(self.banner_list) + 1, 'content': content, 'availability': 'True'} 
            self.banner_list.append(banner_dict)
            return True, 'OK' 
        except:
            return False, 'DATABASE_ERROR'
    

    @require_login    
    def add_welcome(self, session_key, content):
        '''
        관리자용 welcome 추가 함수

        >>> notice.add_welcome(SYSOP_session_key, content)
        True, 'OK'
        >>> notice.add_welcome(user_session_key, content)
        False, 'NOT_SYSOP'
        
        @type  session_key: string
        @param session_key: User Key
        @type  content: string 
        @param content: Welcome Content(html tag)
        @rtype: string
        @return:
            1. welcome 페이지 추가에 성공하였을 때: True, 'OK'
            2. welcome 페이지 추가에 실패하였을 때:
                1. 시삽이 아닐 때: False, 'NOT_SYSOP'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        if not self.member_manager.is_sysop(session_key):
            return False, 'NOT_SYSOP'
        try:
            # DB에서 welcome 관련 해서 데이터 받아오는 부분 추가
            welcome_dict= {'no': len(self.welcome_list) + 1, 'content': content, 'availability': 'True'} 
            self.welcome_list.append(welcome_dict)
            return True, 'OK' 
        except:
            return False, 'DATABASE_ERROR'


    @require_login 
    def remove_banner(self, session_key, no):
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
            '''DB에서 banner 관련 해서 데이터 받아오는 부분 추가'''
            for banner in self.banner_list:
                if banner['no'] == no:
                    banner['availability'] = 'False' 
                    return True, 'OK' 
            return False, 'NOT_EXIST_BANNER'
        except:
            raise
            return False, 'DATABASE_ERROR'
    
    @require_login 
    def remove_welcome(self, session_key, no):
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
            '''DB에서 welcome 관련 해서 데이터 받아오는 부분 추가'''
            for welcome in self.welcome_list:
                if welcome['no'] == no:
                    welcome['availability'] = 'False' 
                    return True, 'OK' 
            return False, 'NOT_EXIST_WELCOME'
        except:
            raise
            return False, 'DATABASE_ERROR'
    


# vim: set et ts=8 sw=4 sts=4
