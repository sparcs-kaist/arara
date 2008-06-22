# -*- coding: utf-8 -*-

class BlacklistManager(object):
    """
    블랙리스트 처리 관련 클래스
    """

    def __init__(self):
        pass

    def add(self, session_key, blacklist_id):
        """
        블랙리스트 id 추가 

        >>> blacklist.add(session_key, "pv457")
	True, "OK"

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_id: string
        @param blacklist_id: Blacklist ID
        @rtype: string
        @return:
            1. 추가 성공: True, "OK"
            2. 추가 실패:
		1. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def delete(self,session_key, blacklist_id):
        """
        블랙리스트 id 삭제 

        >>> blacklist.delete(session_key, "pv457")
	True, "OK"

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_id: string
        @param blacklist_id: Blacklist ID
        @rtype: boolean
        @return:
            1. 삭제 성공: True, "OK"
            2. 삭제 실패:
		1. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
    
    def list(self,session_key):
        """
        블랙리스트로 설정한 사람의 목록을 보여줌

        >>> blacklist.list_show(session_key)
	True, ['pv457', 'serialx', ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 성공: True, Blacklist ID List
	    2. 실패:
		1. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
