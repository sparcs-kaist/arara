# -*- coding: utf-8 -*-

class MessagingManager(object):
    '''
    회원간 쪽지기능등을 담당하는 클래스
    '''

    def __init__(self):
        pass

    def sent_list(self, session_key):
        '''
        보낸 쪽지 리스트 읽어오기

        >>> messaging.sent_list(session_key)
        True, [{'msg_no': 1, 'from': 'pv457', 'to': 'serialx',
        'message_article': '야! 너 북극곰이라며?', 'time_when_sent': '2008.02.13 12:13:43'}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Message List
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

    def receive_list(self, session_key):
        '''
        받은 쪽지 리스트 읽어오기

        >>> messaging.receive_list(session_key)
        True, [{'msg_no': 2, 'from': 'serialx', 'to': 'pv457',
        'message_article': '장난? 아니거등?', 'time_when_sent': '2008.02.13 12:15:32'}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Message List
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        return True, []

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
                1. 보낼 아이디가 존재하지 않음: False, 'to_NOT_EXIST'
                2. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        return True, 'OK'

    def read_message(self, session_key, msg_no):
        '''
        쪽지 하나 읽어오기

        >>> messaging.read_message(session_key, 34)
        True, {'msg_no': 3, 'from': 'pipoket', 'to': 'serialx',
        'message_article': '북극곰 ㅇㅅㅇ', 'time_when_sent': '2008.02.13. 12:17:34'}

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

# vim: set et ts=8 sw=4 sts=4
