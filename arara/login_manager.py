# -*- coding: utf-8 -*-

class LoginManager(object):
    """
    로그인 처리 관련 클래스
    """
    
    def __init__(self):
        pass

    def login(id, password, user_ip):
        """
        로그인 처리를 담당하는 함수.
        아이디와 패스워드를 받은 뒤 User Key를 리턴.

        >>> session_key = login_manager.login(id, pw, "143.248.234.143")

        @type  id: string
        @param id: User ID
        @type  password: string
        @param password: User Passwordi
	@type  user_ip: string
	@param user_ip: User IP
        @rtype: string
        @return: 
            1. 로그인 성공 시: User Key
            2. 로그인 실패 시
		1. 아이디 존재하지 않음: 1
		2. 패스워드 불일치: 2
		3. 데이터베이스 관련 에러: 99

        """

    def logout(session_key):
        """
        로그아웃 처리를 담당하는 함수.

        >>> login_manager.logout(session_key)

        @type  session_key: string
        @param session_key: User Key
        @rtype: integer
        @return:
            1. 로그아웃 성공 시: 0
            2. 로그아웃 실패 시
		1. 로그인되지 않은 사용자: 1
		2. 데이터베이스 관련 에러: 99
        """

    def updatesession(session_key):
	"""
	세션 expire시간을 연장해주는 함수

	>>> login_manager.updatesession(session_key)

        @type  session_key: string
        @param session_key: User Key
        @rtype: integer
        @return:
            1. 업데이트 성공 시: 0
            2. 업데이트 실패 시
		1. 로그인되지 않은 사용자: 1
		2. 데이터베이스 관련 에러: 99
        """
