# -*- coding: utf-8 -*-

import hashlib

global member_dic
global member_no
member_dic = {}

class WrongDictionary(Exception):
    pass

class MemberManager(object):
    """
    회원 가입, 회원정보 수정, 회원정보 조회, 이메일 인증등을 담당하는 클래스
    """

    def __init__(self):
        global member_no
        member_no = len(member_dic)
        pass

    def register(self, user_reg_dic):
        """
        DB에 회원 정보 추가

        >>> member.register(user_reg_dic)
	True, "OK"

	    - Current User Dictionary { ID, password, nickname, email, sig, self_introduce, default_language }

        @type  user_reg_dic: dictionary
        @param user_reg_dic: User Dictionary
        @rtype: string
        @return:
            1. register 성공: True, "OK"
            2. register 실패:
		1. 양식이 맞지 않음(부적절한 NULL값 등): "WRONG_DICTIONARY"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

        global member_no

        user_reg_keys = ["id", "password", "nickname", "email", "sig", "self_introduce", "default_language"]
        tmp_user_dic = {}

        try:
            for key in user_reg_keys:
                if not key in user_reg_dic:
                    raise WrongDictionary()
                tmp_user_dic[key] = user_reg_dic[key]
        except WrongDictionary:
            return False, "WRONG_DICTIONARY"

        tmp_user_dic['activate'] = 'False'
        tmp_user_dic['activate_code'] = hashlib.md5(tmp_user_dic['id']+
                tmp_user_dic['password']+tmp_user_dic['nickname']).hexdigest()
        
        try:
            member_no += 1
            member_dic[member_no] = tmp_user_dic
        except Exception:
            return False, "THIS_EXCEPTION_SHOULD_NEVER_HAPPEN_DURING_DUMMY_CODE"

        return True, member_dic[member_no]['activate_code']


    def confirm(self, id_to_confirm, confirm_key):
        """
        인증코드 확인

        >>> member.confirm( id_to_confirm, confirm_session_key)
	True, "OK"

        @type  confirm_key: integer
        @param confirm_key: Confirm Key
        @rtype: string
        @return:
            1. 인증 성공: True, "OK"
	    2. 인증 실패:
		1. 잘못된 인증코드: False, "WRONG_CONFIRM_KEY"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def is_registered(self, user_id, password):
        #remove quote when MD5 hash for UI is available
        #
        for keys in member_dic:
            if user_id == member_dic[keys]['id']:
                if password = member_dic[keys]['password']:
                    return True, "OK"

    def get_info(self, session_key):
	"""
	회원 정보 수정을 위한 회원 정보를 가져오는 함수, 쿼리와 다름

	>>> member.get_info(logged_in_session_key)
	True, {"id": "serialx", "name": "홍성진", "nickname": "PolarBear", ...}
	>>> member.get_info(NOT_logged_in_session_key)
	False, "NOT_LOGGEDIN"

	@type  session_key: string
	@param session_key: User Key
	@rtype: dictionary
	@return:
	    1. 가져오기 성공: True, user_dic
	    2. 가져오기 실패:
		1. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		2. 존재하지 않는 회원: False, "MEMBER_NOT_EXIST"
		3. 데이터베이스 오류: False, "DATABASE_ERROR"
	"""
        
    def modify_password(self, session_key, user_password_dic):
        """
        DB에 회원 정보 수정

        >>> member.modify(session_key, user_password_dic)
	True, "OK"

	---user_password_dic {id, current_password, new_password}

        @type  session_key: string
        @param session_key: User Key
        @type  user_password_dic: dictionary
        @param user_password_dic: User Dictionary
        @rtype: string
        @return:
            1. modify 성공: True, "OK"
            2. modify 실패:
		1. 수정 권한 없음: "NO_PERMISSION"
		2. 잘못된 현재 패스워드: "WRONG_PASSWORD"
		3. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		4. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def modify(self, session_key, user_reg_dic):
        """
        DB에 회원 정보 수정

        >>> member.modify(session_key, user_reg_dic)
	True, "OK"

        @type  session_key: string
        @param session_key: User Key
        @type  user_reg_dic: dictionary
        @param user_reg_dic: User Dictionary
        @rtype: string
        @return:
            1. modify 성공: True, "OK"
            2. modify 실패:
		1. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def query_by_id(self, session_key, query_id):
	"""
	쿼리 함수

	>>> member.querybyid(session_key, "pv457")
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
		1. 존재하지 않는 아이디: False, "QUERY_ID_NOT_EXIST"
		2. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		3. 데이터베이스 오류: False, "DATABASE_ERROR"
	"""

    def query_by_nick(self, session_key, query_nickname):
	"""
	쿼리 함수

	>>> member.querybynick(session_key, "심영준")
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
		1. 존재하지 않는 닉네임: False, "QUERY_NICK_NOT_EXIST"
		2. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		3. 데이터베이스 오류: False, "DATABASE_ERROR"
	"""
       
    def remove_user(self, session_key):
	"""
	session key로 로그인된 사용자를 등록된 사용자에서 제거한다" - 회원탈퇴

	>>> member.remove_user(logged_session_key)
	True, "OK"
	>>> member.remove_user(not_logged_session_key)
	False, "NOT LOGGEDIN"
	
	@type  session_key: string
	@param session_key: User Key
	@rtype: String
	@return:
	    1. 성공시: True, "OK"
	    2. 실패시: False, "NOT LOGGEDIN"
	"""
