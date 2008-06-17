# -*- coding: utf-8 -*-

class BlacklistManager(object):

    def __init__(self):
        pass

    def add(session_key, blacklist_id):
        """
        블랙리스트 id 추가 

        >>> blacklist.add(session_key, "pv457")

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_id: string
        @param blacklist_id: Blacklist ID
        @rtype: boolean
        @return:
            1. 추가 성공: True
            2. 추가 실패: False
        """

    def delete(session_key, blacklist_id):
        """
        블랙리스트 id 삭제 

        >>> blacklist.delete(session_key, "pv457")

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_id: string
        @param blacklist_id: Blacklist ID
        @rtype: boolean
        @return:
            1. 삭제 성공: True
            2. 삭제 실패: False
        """
    
    def list(session_key):
        """
        블랙리스트로 설정한 사람의 목록을 보여줌

        >>> blacklist.list_show(session_key)

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 성공: Blacklist ID List
            2. 실패: False
        """
