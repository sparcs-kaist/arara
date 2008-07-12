# -*- coding: utf-8 -*-

import md5
from arara.util import require_login
>>>>>>> .r151

class WrongDictionary(Exception):
    pass

class NoPermission(Exception):
    pass

class WrongPassword(Exception):
    pass

class NotLoggedIn(Exception):
    pass


class MemberManager(object):
    '''
    회원 가입, 회원정보 수정, 회원정보 조회, 이메일 인증등을 담당하는 클래스
    '''

    def __init__(self):
        # mock data
        self.member_dic = {}  # DB에서 member table를 read해오는 부분

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _authenticate(self, id, pw):
        try:
            if self.member_dic[id]['password'] == pw:
                return True, None
            else:
                return False, 'WRONG_PASSWORD'
        except KeyError:
            return False, 'WRONG_ID'


    def register(self, user_reg_dic):
        '''
        DB에 회원 정보 추가. activation code를 발급한다.

        >>> user_reg_dic = { 'id':'mikkang', 'password':'mikkang', 'nickname':'mikkang', 'email':'mikkang', 'sig':'mikkang', 'self_introduce':'mikkang', 'default_language':'english' }
        >>> member_manager.register(user_reg_dic)
        (True, '12tge8r9ytu23oytw8')

        - Current User Dictionary { id, password, nickname, email, sig, self_introduce, default_language }

        @type  user_reg_dic: dictionary
        @param user_reg_dic: User Dictionary
        @rtype: string
        @return:
            1. register 성공: True, self.member_dic[user_reg_dic['id']]['activate_code']
            2. register 실패:
                1. 양식이 맞지 않음(부적절한 NULL값 등): 'WRONG_DICTIONARY'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        user_reg_keys = ['id', 'password', 'nickname', 'email', 'sig', 'self_introduce', 'default_language']
        tmp_user_dic = {}

        try:
            for key in user_reg_keys:
                if not key in user_reg_dic:
                    raise WrongDictionary()
                tmp_user_dic[key] = user_reg_dic[key]
        except WrongDictionary:
            return False, 'WRONG_DICTIONARY'

        tmp_user_dic['activate'] = 'False'
        tmp_user_dic['activate_code'] = md5.md5(tmp_user_dic['id']+
                tmp_user_dic['password']+tmp_user_dic['nickname']).hexdigest()
        
        try:
            self.member_dic[user_reg_dic['id']] = tmp_user_dic
        except Exception:
            return False, 'THIS_EXCEPTION_SHOULD_NEVER_HAPPEN_DURING_DUMMY_CODE'

        return True, self.member_dic[user_reg_dic['id']]['activate_code']


    def confirm(self, id_to_confirm, confirm_key):
        '''
        인증코드(activation code) 확인.

        >>> member_manager.confirm('mikkang', register_key)
        (True, 'OK')
        >>> member_manager.confirm('mikkang', 'asdfasdfasdfsd')
        (False, 'WRONG_CONFIRM_KEY')

        @type  id_to_confirm: string
        @param id_to_confirm: Confirm ID
        @type  confirm_key: integer
        @param confirm_key: Confirm Key
        @rtype: string
        @return:
            1. 인증 성공: True, 'OK'
            2. 인증 실패:
                1. 잘못된 인증코드: False, 'WRONG_CONFIRM_KEY'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        try:
            if self.member_dic[id_to_confirm]['activate_code'] == confirm_key:
                self.member_dic[id_to_confirm]['activate'] = True
                return True, 'OK'
        except KeyError:
            return False, 'WRONG_CONFIRM_KEY'
        

    def is_registered(self, user_id):
        '''
        등록된 사용자인지의 여부를 알려준다.
        Confirm은 하지 않았더라도 등록되어있으면 True를 리턴한다.

        @type  user_id: string
        @param user_id: ID to check whether is registered or not
        @rtype: bool
        @return:
            1. 존재하는 사용자: True
            2. 존재하지 않는 사용자: False

        >>> member_manager.is_registered('mikkang')
        True
        '''
        #remove quote when MD5 hash for UI is available
        #
        return self.member_dic.has_key(user_id)

    def get_info(self, session_key):
        '''
        회원 정보 수정을 위해 현재 로그인된 회원의 정보를 가져오는 함수.
        다른 사용자의 정보를 열람하는 query와 다름.

        @type  session_key: string
        @param session_key: User Key
        @rtype: dictionary
        @return:
            1. 가져오기 성공: True, user_dic
            2. 가져오기 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 존재하지 않는 회원: False, 'MEMBER_NOT_EXIST'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        try:
            import sys
            return True, self.member_dic[self.login_manager.get_session(session_key)[1]['id']]
        except KeyError:
            return False, "MEMBER_NOT_EXIST"

        
    def modify_password(self, session_key, user_password_dic):
        '''
        회원의 password를 수정.

        ---user_password_dic {id, current_password, new_password}

        @type  session_key: string
        @param session_key: User Key
        @type  user_password_dic: dictionary
        @param user_password_dic: User Dictionary
        @rtype: string
        @return:
            1. modify 성공: True, 'OK'
            2. modify 실패:
                1. 수정 권한 없음: 'NO_PERMISSION'
                2. 잘못된 현재 패스워드: 'WRONG_PASSWORD'
                3. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                4. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        session_info = self.login_manager.get_session(session_key)[1]
        try:
            if not session_info['id'] == user_password_dic['id']:
                raise NoPermission()
            if not self.member_dic[session_info['id']]['password'] == user_password_dic['current_password']:
                raise WrongPassword()
            self.member_dic[session_info['id']]['password'] = user_password_dic['new_password']
            return True, 'OK'
            
        except NoPermission:
            return False, 'NO_PERMISSION'

        except WrongPassword:
            return False, 'WRONG_PASSWORD'

        except KeyError:
            return False, 'NOT_LOGGEDIN'


    @require_login
    def modify(self, session_key, user_reg_dic):
        '''
        password를 제외한 회원 정보 수정

        @type  session_key: string
        @param session_key: User Key
        @type  user_reg_dic: dictionary
        @param user_reg_dic: User Dictionary
        @rtype: string
        @return:
            1. modify 성공: True, 'OK'
            2. modify 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
                3. 양식이 맞지 않음(부적절한 NULL값 등): 'WRONG_DICTIONARY'
        '''

        user_reg_keys = ['id', 'password', 'nickname', 'email', 'sig', 'self_introduce', 'default_language']
        tmp_user_dic = {}
        try:
            for key in user_reg_keys:
                if not key in user_reg_dic:
                    raise WrongDictionary()
                tmp_user_dic[key] = user_reg_dic[key]
        except WrongDictionary:
            return False, 'WRONG_DICTIONARY'
        self.member_dic[user_reg_dic['id']] = tmp_user_dic
        return True, 'OK'

    def query_by_id(self, session_key, query_id):
        '''
        쿼리 함수

        member.query_by_id(session_key, 'pv457')
        True, {'user_id': 'pv457', 'user_nickname': '심영준',
        'self_introduce': '...', 'user_ip': '143.248.234.111'}

        ---query_dic { user_id, user_nickname, self_introduce, user_ip }

        @type  session_key: string
        @param session_key: User Key
        @type  query_id: string
        @param query_id: User ID to send Query
        @rtype: dictionary
        @return:
            1. 쿼리 성공: True, query_dic
            2. 쿼리 실패:
                1. 존재하지 않는 아이디: False, 'QUERY_ID_NOT_EXIST'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

    def query_by_nick(self, session_key, query_nickname):
        '''
        쿼리 함수

        member.query_by_nick(session_key, '심영준')
        True, {'user_id': 'pv457', 'user_nickname': '심영준',
        'self_introduce': '...', 'user_ip': '143.248.234.111'}

        ---query_dic { user_id, user_nickname, self_introduce, user_ip }

        @type  session_key: string
        @param session_key: User Key
        @type  query_nickname: string
        @param query_nickname: User Nickname to send Query
        @rtype: dictionary
        @return:
            1. 쿼리 성공: True, query_dic
            2. 쿼리 실패:
                1. 존재하지 않는 닉네임: False, 'QUERY_NICK_NOT_EXIST'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
       
    def remove_user(self, session_key):
        '''
        session key로 로그인된 사용자를 등록된 사용자에서 제거한다' - 회원탈퇴

        @type  session_key: string
        @param session_key: User Key
        @rtype: String
        @return:
            1. 성공시: True, 'OK'
            2. 실패시: False, 'NOT_LOGGEDIN'
        '''
        try:
            self.member_dic.pop(self.login_manager.session_dic[session_key]['id'])
            return True, 'OK'

        except KeyError:
            return False, 'NOT_LOGGEDIN'
        
    @require_login
    def search_user(self, session_key, search_user_info):
        '''
        member_dic 에서 찾고자 하는 id와 nickname에 해당하는 user를 찾아주는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  search_user_info: dictionary
        @param search_user_info: User Info(id or nickname)
        @rtype: String
        @return:
            1. 성공시: True, USER_ID 
            2. 실패시: False, 'NOT_EXIST_USER'
        '''

        try:
            assert len(search_user_info.keys()) == 1
            key = search_user_info.keys()[0]
            value = search_user_info.values()[0]
            assert key == 'id' or key == 'nickname'
            for id, info in self.member_dic.items():
                if value in info[key]:
                    return True, id
            return False, 'NOT_EXIST_USER'
        except AssertionError:
            pass

    @require_login
    def is_sysop(self, session_key):
        '''
        로그인한 user가 SYSOP인지 아닌지를 확인하는 함수
        
        @type  session_key: string
        @param session_key: User Key
        @rtype: String
        @return:
            1. SYSOP일시: True
            2. SYSOP이 아닐시: False
        '''

        if self.login_manager.get_session(session_key)[1]['id'] == 'SYSOP':
            return True
        else:
            return False

# vim: set et ts=8 sw=4 sts=4
