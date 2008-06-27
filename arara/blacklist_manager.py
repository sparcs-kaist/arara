# -*- coding: utf-8 -*-

from login_manager import *

global blacklist
blacklist = {}

class AlreadyAddedException(Exception):
    pass

class NotExistIDException(Exception):
    pass

class NotLoggedIn(Exception):
    pass

class BlacklistManager(object):
    """
    블랙리스트 처리 관련 클래스
    """
    def __init__(self):
        global blacklist
        global Login
        Login = LoginManager()
        pass

    def add(self, session_key, blacklist_id):
        """
        블랙리스트 id 추가

        default 값: article과 message 모두 True

        저장 형태: { "pv457": {"article": "True", "message": "False"}} 

        >>> blacklist.add(session_key,"pv457")
        True, "OK"

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_id: stirng
        @param blacklist_id: Blacklist ID 
        @rtype: boolean, string
        @return:
            1. 추가 성공: True, "OK"
            2. 추가 실패:
                1. 존재하지 않는 아이디: False, "ID_NOT_EXIST"
                2. 이미 추가되어있는 아이디: False, "ALREADY_ADDED"
                3. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
                4. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
        global blacklist
        global Login

        try:
            if not Login.is_logged_in(session_id):
                raise NotLoggedIn ()
        except NotLoggedIn:
            return False, "NOT_LOGGEDIN"
        
        try:
            if blacklist_id in blacklist:
                raise AlreadyAddedException()
            blacklist[blacklist_id] = {"article": "True", "message": "True"}
            return True, "OK"
        except AlreadyAddedException:
            return False, "ALREADY_ADDED_ID"        
            
    def delete(self,session_key, blacklist_id):
        """
        블랙리스트 id 삭제 

        >>> blacklist.delete(session_key, "pv457")
        True, "OK"

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_id: string
        @param blacklist_id: Blacklist ID
        @rtype: boolean, string
        @return:
            1. 삭제 성공: True, "OK"
            2. 삭제 실패:
                1. 존재하지 않는 아이디: False, "ID_NOT_EXIST"
                2. 블랙리스트에 존재하지 않는 아이디: False, "ID_NOT_IN_BLACKLIST"
                3. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
                4. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
        global blacklist
        global Login

        try:
            if not Login.is_logged_in(session_id):
                raise NotLoggedIn ()
        except NotLoggedIn:
            return False, "NOT_LOGGEDIN"
        
        
        try:
            if blacklist_id not in blacklist:
                raise NotExistIDException()
            del blacklist[blacklist_id]
        except NotExistIDException:
            return False, "ID_NOT_IN_BLACKLIST"        


    def modify(self,session_key, blacklist_dic):
        """
        블랙리스트 id 수정 

        >>> blacklist.modify(session_key, {"id": "pv457", 
        "article": "False", "message": "True"})
        True, "OK"

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_dic: dictionary
        @param blacklist_dic: Blacklist Dictionary
        @rtype: boolean, string
        @return:
            1. 삭제 성공: True, "OK"
            2. 삭제 실패:
                1. 블랙리스트에 존재하지 않는 아이디: False, "ID_NOT_IN_BLACKLIST"
                2. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
                3. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
        global blacklist
        global Login

        try:
            if not Login.is_logged_in(session_id):
                raise NotLoggedIn ()
        except NotLoggedIn:
            return False, "NOT_LOGGEDIN"
        

        try:
            if blacklist_id not in blacklist:
                raise NotExistIDException()
            blacklist[blacklist_id] = {"article": blacklist_dic["article"], "message": blacklist_dic["message"]}
            return True, "OK"
        except NotExistIDException:
            return False, "ID_NOT_IN_BLACKLIST"        


    def list(self,session_key):
        """
        블랙리스트로 설정한 사람의 목록을 보여줌

        >>> blacklist.list_show(session_key)
        True, [{"id": "pv457", "article": "True", "message" False"},
        {"id": "serialx", "article": "False", "message", "True"}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, list
        @return:
            1. 성공: True, Blacklist Dictionary List
            2. 실패:
                1. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
                2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
        global blacklist
        global Login

        try:
            if not Login.is_logged_in(session_id):
                raise NotLoggedIn ()
        except NotLoggedIn:
            return False, "NOT_LOGGEDIN"
        
        
        return True, blacklist
