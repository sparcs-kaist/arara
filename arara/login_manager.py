# -*- coding: utf-8 -*-

class LoginManager(object):
    """
    로그인 처리 관련 클래스
    """
    
    def __init__(self):
        pass

    def login(id, password):
        """
        로그인 처리를 담당하는 함수.
        아이디와 패스워드를 받은 뒤 User Key를 리턴.

        >>> session_key = login_manager.login(id, pw)

        >>> article.read(session_key, 300)

        @type  id: string
        @param id: User ID
        @type  password: string
        @param password: User Password
        @rtype: string
        @return: 
            1. 로그인 성공 시: User Key
            2. 로그인 실패 시: False
        """

    def logout(session_key):
        """
        로그아웃 처리를 담당하는 함수.

        >>> login_manager.logout(session_key)

        @type  session_key: string
        @param session_key: User Key
        @rtype: string
        @return:
            1. 로그아웃 성공 시: True
            2. 로그아웃 실패 시: False
        """

