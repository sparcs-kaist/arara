# -*- coding: utf-8 -*-

class AlreadyAddedException(Exception):
    pass

class NotExistusernameException(Exception):
    pass

class NotLoggedIn(Exception):
    pass

class BlacklistManager(object):
    '''
    블랙리스트 처리 관련 클래스
    '''
    def __init__(self):
        # will make list for blacklist member in member_dic, key value is blacklist ex)59
        self.member_dic = {}

    def _require_login(function):
        def wrapper(self, session_key, *args):
            if not self.login_manager.is_logged_in(session_key):
                return False, 'NOT_LOGGEDIN'
            else:
                return function(self, session_key, *args)
        return wrapper

    def _prepare_session_username(function):
        # Internal member_dic에 사용자 username를 강제 등록한다.
        def wrapper(self, session_key, *args):
            if not self.member_dic.has_key(self.login_manager.get_session(session_key)[1]['username']):
                self.member_dic[self.login_manager.get_session(session_key)[1]['username']] = {}
            return function(self, session_key, *args)
        return wrapper

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _set_member_manager(self, member_manager):
        self.member_manager = member_manager

    @_prepare_session_username
    @_require_login
    def add(self, session_key, blacklist_username):
        '''
        블랙리스트 username 추가

        default 값: article과 message 모두 True

        저장 형태: { 'pv457': {'article': 'True', 'message': 'False'}} 

        >>> blacklist.add(session_key,'pv457')
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_username: stirng
        @param blacklist_username: Blacklist username 
        @rtype: boolean, string
        @return:
            1. 추가 성공: True, 'OK'
            2. 추가 실패:
                1. 존재하지 않는 아이디: False, 'USERNAME_NOT_EXIST'
                2. 이미 추가되어있는 아이디: False, 'ALREADY_ADDED'
                3. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                4. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        session_username = self.login_manager.get_session(session_key)[1]['username']
        try:
            if self.member_manager.is_registered(blacklist_username) == False:
                raise NotExistusernameException()
            if blacklist_username in self.member_dic[session_username]:
                raise AlreadyAddedException()
            self.member_dic[session_username][blacklist_username] = {'article': 'True', 'message': 'True'}
            return True, 'OK'
        except AlreadyAddedException:
            return False, 'ALREADY_ADDED'
        except NotExistusernameException:
            return False, 'USERNAME_NOT_EXIST'
       
    @_prepare_session_username
    @_require_login
    def delete(self,session_key, blacklist_username):
        '''
        블랙리스트 username 삭제 

        >>> blacklist.delete(session_key, 'pv457')
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_username: string
        @param blacklist_username: Blacklist username
        @rtype: boolean, string
        @return:
            1. 삭제 성공: True, 'OK'
            2. 삭제 실패:
                1. 블랙리스트에 존재하지 않는 아이디: False, 'USERNAME_NOT_IN_BLACKLIST'
                2. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        session_username =  self.login_manager.get_session(session_key)[1]['username']
        try:
            if blacklist_username not in self.member_dic[session_username]:
                raise NotExistusernameException()
            del self.member_dic[session_username][blacklist_username] 
            return True, 'OK'
        except NotExistusernameException:
            return False, 'USERNAME_NOT_IN_BLACKLIST'        


    @_prepare_session_username
    @_require_login
    def modify(self,session_key, blacklist_dic):
        '''
        블랙리스트 username 수정 

        >>> blacklist.modify(session_key, {'username': 'pv457', 
        'article': 'False', 'message': 'True'})
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
        @type  blacklist_dic: dictionary
        @param blacklist_dic: Blacklist Dictionary
        @rtype: boolean, string
        @return:
            1. 수정 성공: True, 'OK'
            2. 수정 실패:
                1. 블랙리스트에 존재하지 않는 아이디: False, 'USERNAME_NOT_IN_BLACKLIST'
                2. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        
        session_username =  self.login_manager.get_session(session_key)[1]['username']
        try:
            if blacklist_dic['username'] not in self.member_dic[session_username]:
                raise NotExistusernameException()
            self.member_dic[session_username][blacklist_dic['username']] = {'article': blacklist_dic['article'], 'message': blacklist_dic['message']}
            return True, 'OK'
        except NotExistusernameException:
            return False, 'USERNAME_NOT_IN_BLACKLIST'        

    @_prepare_session_username
    @_require_login
    def list(self,session_key):
        '''
        블랙리스트로 설정한 사람의 목록을 보여줌

        >>> blacklist.list_show(session_key)
        True, [{'username': 'pv457', 'article': 'True', 'message' False'},
        {'username': 'serialx', 'article': 'False', 'message', 'True'}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, list
        @return:
            1. 성공: True, Blacklist Dictionary List
            2. 실패:
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        session_username =  self.login_manager.get_session(session_key)[1]['username']
        ret = []
        for username, values in self.member_dic[session_username].items():
            r = {'username': username}
            r.update(values)
            ret.append(r)
            
        return True, ret

# vim: set et ts=8 sw=4 sts=4
