# -*- coding: utf-8 -*-

import md5 as hashlib
import datetime

class LoginManager(object):
    '''
    로그인 처리 관련 클래스
    '''
    
    def __init__(self):
        self.session_dic = {}

    def login(self, id, password, user_ip):
        '''
        로그인 처리를 담당하는 함수.
        아이디와 패스워드를 받은 뒤 User Key를 리턴.

        >>> session_key = login_manager.login(id, pw, '143.248.234.143')
        True, '6bd89dab95356'
        >>> session_key = login_manager.login(id, wrong_pw, '143.248.234.143')
        False, 'WRONG_PASSWORD'

        @type  id: string
        @param id: User ID
        @type  password: string
        @param password: User Passwordi
        @type  user_ip: string
        @param user_ip: User IP
        @rtype: string
        @return: 
            1. 로그인 성공 시: True, user_key
            2. 로그인 실패 시
                1. 아이디 존재하지 않음: False, 'WRONG_ID'
                2. 패스워드 불일치: False, 'WRONG_PASSWORD'
                3. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'

        '''
        

        if(id == 'test'):
            if(password == 'test'):
                hash = hashlib.md5(id+password).hexdigest()
                timestamp = datetime.datetime.isoformat(datetime.datetime.now())
                self.session_dic[hash] = {'id': id, 'ip': user_ip, 'logintime': timestamp}
                return True, hash
            else:
                return False, 'WRONG_PASSWORD'
        else:
            return False, 'WRONG_ID'


    def logout(self, session_key):
        '''
        로그아웃 처리를 담당하는 함수.

        >>> login_manager.logout(logged_in_session_key)
        True, 'OK'
        >>> login_manager.logout(NOT_logged_in_session_key)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @rtype: string
        @return:
            1. 로그아웃 성공 시: True, 'OK'
            2. 로그아웃 실패 시
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'
        '''

        

        try:
            self.session_dic.pop(session_key)
            return True, 'OK'
        except KeyError:
            return False, 'NOT_LOGGEDIN'

    def update_session(self, session_key):
        '''
        세션 expire시간을 연장해주는 함수

        >>> login_manager.update_session(logged_in_session_key)
        True, 'OK'
        >>> login_manager.update_session(NOT_logged_in_session_key)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @rtype: integer
        @return:
            1. 업데이트 성공 시: True, 'OK'
            2. 업데이트 실패 시
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'
        '''

        return False, 'NOT_IMPLEMENTED'

    def is_logged_in(self, session_key):
        '''
        로그인 여부를 체크하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: string
        @return:
            1. 로그인 되어있을 경우: True, self.session_dic {id, user_ip, login_time}
            2. 로그인 되어있지 않을 경우: False, 'NOT_LOGGEDIN'
        '''

        try:
            session_info = self.session_dic[session_key]
            return True, session_info
        except KeyError:
            return False, 'NOT_LOGGEDIN'
