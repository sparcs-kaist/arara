# -*- coding: utf-8 -*-
import datetime
import time

from arara.util import require_login, filter_dict
from arara import model
from sqlalchemy.exceptions import InvalidRequestError

MESSAGE_WHITELIST = ['id', 'from', 'to', 'message', 'sent_time', 'read_status']

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

    def _get_dict(self, item):
        item_dict = item.__dict__
        if item_dict['from_id']:
            item_dict['from'] = item.from_user.username
            del item_dict['from_id']
        if item_dict['to_id']:
            item_dict['to'] = item.to_user.username
            del item_dict['to_id']
        filtered_dict = filter_dict(item_dict, MESSAGE_WHITELIST)

        return filtered_dict

    def _get_dict_list(self, raw_list):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item)
            return_list.append(filtered_dict)
        return return_list


    @require_login
    def sent_list(self, session_key, page=1, page_length=20):
        '''
        보낸 쪽지 리스트 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @type  page: integer
        @param page: Page Number
        @type  page_length: integer
        @param page_length: Number of Messages to get in one page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Message List(보낸쪽지가 없을 경우 [] return)
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        session = model.Session()
        sent_user = session.query(model.User).filter_by(username=user_info['username']).one()

        offset = page_length * (page - 1)
        last = offset + page_length
        sent_messages = sent_user.send_messages[::-1][offset:last]
        sent_messages_dict_list = self._get_dict_list(sent_messages)
        return True, sent_messages_dict_list


    @require_login
    def receive_list(self, session_key, page=1, page_length=20):
        '''
        받은 쪽지 리스트 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @type  page: integer
        @param page: Page Number
        @type  page_langth: integer
        @param page_length: Number of Messages to get in one page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Message List
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        session = model.Session()
        to_user = session.query(model.User).filter_by(username=user_info['username']).one()
        
        offset = page_length * (page - 1)
        last = offset + page_length
        received_messages = to_user.received_messages[::-1][offset:last]
        received_messages_dict_list = self._get_dict_list(received_messages)
        return True, received_messages_dict_list

    @require_login
    def send_message(self, session_key, to, msg):
        '''
        쪽지 전송하기

        @type  session_key: string
        @param session_key: User Key
        @type  to: string
        @param to: Destination username
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
        session = model.Session()
        from_user = session.query(model.User).filter_by(username=user_info['username']).one()
        from_user_ip = user_info['ip']
        to_user = session.query(model.User).filter_by(username=to).one()
        message = model.Message(from_user, from_user_ip, to_user, msg)
        try:
            session.save(message)
            session.commit()
        except InvalidRequestError:
            return False, "DATABASE_ERROR"
        return True, 'OK'

    @require_login
    def read_message(self, session_key, msg_no):
        '''
        쪽지 하나 읽어오기

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
        
        ret, user_info = self.login_manager.get_session(session_key)
        session = model.Session()
        to_user = session.query(model.User).filter_by(username=user_info['username']).one()
        try:
            message = session.query(model.Message).filter_by(to_id=to_user.id, id=msg_no).one()
        except InvalidRequestError:
            return False, "MSG_NOT_EXIST"
        message_dict = self._get_dict(message)
        message.read_status = 'R'
        session.commit()
        return True, message_dict

# vim: set et ts=8 sw=4 sts=4
