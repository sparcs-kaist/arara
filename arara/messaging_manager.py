# -*- coding: utf-8 -*-
import datetime
import time

from arara.util import require_login

class MessagingManager(object):
    '''
    회원간 쪽지기능등을 담당하는 클래스
    '''

    def __init__(self):
        self.message_list = []

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _set_member_manager(self, member_manager):
        self.member_manager = member_manager

    @require_login
    def sent_list(self, session_key):
        '''
        보낸 쪽지 리스트 읽어오기

        >>> messaging.sent_list(session_key)
        True, [{'msg_no': 1, 'from': 'pv457', 'to': 'serialx',
        'message': '야! 너 북극곰이라며?', 'sent_time': '2008.02.13 12:13:43'}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Message List(보낸쪽지가 없을 경우 [] return)
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret, user_info = self.login_manager.get_session(session_key)
        assert ret
        user_id = user_info['id']
        sent_messages = filter(lambda x: x['from'] == user_id, self.message_list)
        return True, sent_messages


    @require_login
    def receive_list(self, session_key):
        '''
        받은 쪽지 리스트 읽어오기

        >>> messaging.receive_list(session_key)
        True, [{'msg_no': 2, 'from': 'serialx', 'to': 'pv457',
        'message': '장난? 아니거등?', 'sent_time': '2008.02.13 12:15:32'}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Message List
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret, user_info = self.login_manager.get_session(session_key)
        assert ret
        user_id = user_info['id']
        receive_messages = filter(lambda x: x['to'] == user_id, self.message_list)
        return True, receive_messages

    @require_login
    def send_message(self, session_key, to, msg):
        '''
        쪽지 전송하기

        >>> messaging.send_message(session_key, 'pv457', 'hello, world')
        True, 'OK'

        @type  session_key: string
        @param session_key: User Key
        @type  to: string
        @param to: Destination ID
        @type  msg: string
        @param msg: Message string
        @rtype: string
        @return:
            1. 메세지 전송 성공: True, 'OK'
            2. 메세지 전송 실패:
                1. 보낼 아이디가 존재하지 않음: False, 'USER_NOT_EXIST'
                2. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        ret, user_info = self.login_manager.get_session(session_key)
        if not self.member_manager.is_registered(to):
            return False, 'USER_NOT_EXIST'
        from_id = user_info['id']
        time_str = str(datetime.datetime.fromtimestamp(time.time()))

        msg_dict = {'from': from_id, 'to': to, 'message': msg,
                'sent_time': time_str, 'msg_no': len(self.message_list) + 1}

        self.message_list.append(msg_dict)

        return True, 'OK'

    @require_login
    def read_message(self, session_key, msg_no):
        '''
        쪽지 하나 읽어오기

        >>> messaging.read_message(session_key, 34)
        True, {'msg_no': 3, 'from': 'pipoket', 'to': 'serialx',
        'message': '북극곰 ㅇㅅㅇ', 'sent_time': '2008.02.13. 12:17:34'}

        @type  session_key: string
        @param session_key: User Key
        @type  msg_no: integer
        @param msg_no: Message Number
        @rtype: dictionary
        @return:
            1. 읽어오기 성공: True, Message Dictionary
            2. 읽어오기 실패:
                1. 메세지가 존재하지 않음: False, 'MSG_NOT_EXIST'
                2. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        for message in self.message_list:
            if message['msg_no'] == msg_no:
                return True, message
        return False, 'MSG_NOT_EXIST'

# vim: set et ts=8 sw=4 sts=4
