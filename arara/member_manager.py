# -*- coding: utf-8 -*-

class MemberManager(object):
    """
    회원 가입, 회원정보 수정, 회원정보 조회, 이메일 인증등을 담당하는 클래스
    """

    def __init__(self):
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
		1. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def confirm(self, confirm_key):
        """
        인증코드 확인

        >>> member.confirm(confirm_session_key)
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
        
