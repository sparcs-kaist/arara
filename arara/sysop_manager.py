# -*- coding: utf-8 -*-

class SysopManager(object):
    '''
    시샵을 위한 클래스
    '''
    def __init__(self):
        pass

    def add_board(self, session_key, boardname):
        '''
        새 보드를 추가하는 함수

        >>> sysop.add_borad(logged_session_key, boardname)
        True, 'OK'
        >>> sysop.add_board(not_logged_session_key, boardname)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  boardname: string
        @param boardname: New Board Name
        @rtype: string
        @return:
            1. 새 보드 추가 성공시: True, 'OK'
            2. 새 보드 추가 실패시: Fale, 'NOT_LOGGEDIN'
        '''

    def remove_board(self, session_key, boardname):
        '''
        기존의 보드를 없애는 함수

        >>> sysop.remove_board(logged_session_key, boardname)
        True, 'OK'
        >>> sysop.remove_board(not_logged_session_key, boardname)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  boardname: string
        @param boardname: Remove Board Name
        @rtype: string
        @return:
            1.보드 삭제 성공시: True, 'OK'
            2.보드 삭제 실패시: False, 'NOT_LOGGEDIN'
        '''

    def view_user_log(self, session_key, user_id):
        '''
        입력된 유저의 모든 log를 보여주는 함수

        >>> sysop.view_user_log(logged_session_key, user_id)
        True, 'LOG_LIST'
        >>> sysop.view_user_log(not_logged_session_key, user_id)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  user_id: string
        @param user_id: User_id 
        @rtype: String
        @return:
            1.성공시: True, 'LOG_LIST'
            2.실패시: False, 'NOT_LOGGEDIN'
        '''


    def view_ip_log(self, session_key, ip_address):
        '''
        입력된 ip의 모든 log를 보여주는 함수

        >>> sysop.view_ip_log(logged_session_key, ip_address)
        True, 'LOG_LIST'
        >>> sysop.view_ip_log(not_logged_session_key, ip_address)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  ip_address: string
        @param ip_address: Ip_address
        @rtype: String
        @return:
            1.성공시: True, 'LOG_LIST'
            2.실패시: False, 'NOT_LOGGEDIN'
        '''


    def view_date_log(self, session_key, date):
        '''
        입력된 date 모든 log를 보여주는 함수

        >>> sysop.view_user_log(logged_session_key, date)
        True, 'LOG_LIST'
        >>> sysop.view_date_log(not_logged_session_key, date)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  date: string
        @param date: Date
        @rtype: String
        @return:
            1.성공시: True, 'LOG_LIST'
            2.실패시: False, 'NOT_LOGGEDIN'
        '''

    def set_password(self, session_key, user_id, password):
        '''
        입력된 id의 패스워드를 설정한 값으로 초기화화는 함수

        >>> sysop.set_password(logged_session_key, user_id, password)
        True, 'OK'
        >>> sysop.set_password(not_logged_session_key, user_id, password)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  user_id: string
        @param user_id: User ID 
        @type  password: string
        @param password: New Password
        @rtype: string
        @return:
            1.성공시: True, 'OK'
            2.실패시: False, 'NOT_LOGGEDIN'
        '''

    def conform_id_validation(self, session_key, user_id):
        '''
        입력된 id의 유저를 정식 등록된 유저로 설정하는 함수 

        >>> sysop.conform_id_validation(logged_session_key, user_id)
        True, 'OK'
        >>> sysop.conform_id_validation(not_logged_session_key, user_id)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  user_id: string
        @param user_id: User ID 
        @rtype: string
        @return:
            1.성공시: True, 'OK'
            2.실패시: False, 'NOT_LOGGEDIN'
        '''

    def remove_modify_log(self, session_key, board_name, article_no):
        '''
        글 수정 로그를 지우는 함수 

        >>> sysop.remove_modify_log(logged_session_key, board_name, article_no)
        True, 'OK'
        >>> sysop.remove_modify_log(not_logged_session_key, boaord_name, artircle_no)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @type  article_no: number 
        @param article_no: Article Number 
        @rtype: string
        @return:
            1.성공시: True, 'OK'
            2.실패시: False, 'NOT_LOGGEDIN'
        '''


    def remove_user(self, session_key, user_id):
        '''
        session_key가 SYSOP일때 한하여 user_id 사용자를 등록된 사용자에서 제거하는 함수

        >>> sysop.remove_user(logged_session_key, user_id)
        True, 'OK'
        >>> sysop.remove_user(not_logged_session_key, user_id)
        False, 'NOT_LOGGEDIN'

        @type  session_key: string
        @param session_key: User Key
        @type  user_id: string 
        @param user_id: User ID 
        @rtype: string
        @return:
            1.성공시: True, 'OK'
            2.실패시: False, 'NOT_LOGGEDIN'
        '''

# vim: set et ts=8 sw=4 sts=4
