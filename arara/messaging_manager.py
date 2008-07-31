# -*- coding: utf-8 -*-
import datetime
import time

from arara.util import require_login, filter_dict
from arara import model
from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import or_, not_, and_

MESSAGE_WHITELIST = ['id', 'from', 'to', 'message', 'sent_time', 'read_status', 'blacklisted']

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

    def _set_blacklist_manager(self, blacklist_manager):
        self.blacklist_manager = blacklist_manager

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        if item_dict.has_key('from_id'):
            item_dict['from'] = item.from_user.username
            del item_dict['from_id']
        if item_dict.has_key('to_id'):
            item_dict['to'] = item.to_user.username
            del item_dict['to_id']
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
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
        sent_messages_count = session.query(model.Message).filter(and_(model.message_table.c.from_id==sent_user.id, not_(model.message_table.c.sent_deleted==True))).count()
        last_page = int(sent_messages_count / page_length) + 1
        if page > last_page:
            return False, 'WRONG_PAGENUM'
        offset = page_length * (page - 1)
        last = offset + page_length
        sent_messages = session.query(model.Message).filter(and_(model.message_table.c.from_id==sent_user.id, not_(model.message_table.c.sent_deleted==True)))[::-1][offset:last]
        sent_messages_dict_list = self._get_dict_list(sent_messages, MESSAGE_WHITELIST)
        sent_messages_dict_list.append({'last_page': last_page})
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
        _, blacklist_dict_list = self.blacklist_manager.list(session_key)
        blacklist_users = set()
        for blacklist_item in blacklist_dict_list:
            if blacklist_item['block_message']:
                blacklist_users.add(blacklist_item['blacklisted_user_username'])
        received_messages_count = session.query(model.Message).filter(and_(model.message_table.c.to_id==to_user.id, not_(model.message_table.c.received_deleted==True))).count()
        last_page = int(received_messages_count / page_length) + 1
        if page > last_page:
            return False, 'WRONG_PAGENUM'
        offset = page_length * (page - 1)
        last = offset + page_length
        received_messages = session.query(model.Message).filter(not_(model.message_table.c.received_deleted==True))[::-1][offset:last]
        received_messages_dict_list = self._get_dict_list(received_messages, MESSAGE_WHITELIST)
        for item in received_messages_dict_list:
            if item['from'] in blacklist_users:
                item['blacklisted'] = True
            else:
                item['blacklisted'] = False
        received_messages_dict_list.append({'last_page': last_page})
        return True, received_messages_dict_list

    @require_login
    def send_message(self, session_key, to_data, msg):
        '''
        쪽지 전송하기
        보내는 사람 항목인 to에는 한 명의 아이디 혹은 아이디의 리스트를 보낼 수 있음

        @type  session_key: string
        @param session_key: User Key
        @type  to_data: string, list
        @param to_data: Destination username
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
        if type(to_data) == list:
            ret = []
            for to in to_data: 
                if self.member_manager.is_registered(to):
                    session = model.Session()
                    from_user = session.query(model.User).filter_by(username=user_info['username']).one()
                    from_user_ip = user_info['ip']
                    to_user = session.query(model.User).filter_by(username=to).one()
                    message = model.Message(from_user, from_user_ip, to_user, msg)
                    try:
                        session.save(message)
                        session.commit()
                        ret.append('OK')
                    except InvalidRequestError:
                        return False, "DATABASE_ERROR"
                else:
                    ret.append('USER_NOT_EXIST')
            return True, ret
        else:
            if not self.member_manager.is_registered(to_data):
                return False, 'USER_NOT_EXIST'
            session = model.Session()
            from_user = session.query(model.User).filter_by(username=user_info['username']).one()
            from_user_ip = user_info['ip']
            to_user = session.query(model.User).filter_by(username=to_data).one()
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
            message = session.query(model.Message).filter(and_(model.message_table.c.to_id==to_user.id, model.message_table.c.id==msg_no, not_(model.message_table.c.received_deleted==True))).one()
        except InvalidRequestError:
            return False, "MSG_NOT_EXIST"
        message_dict = self._get_dict(message, MESSAGE_WHITELIST)
        message.read_status = u'R'
        session.commit()
        return True, message_dict

    @require_login
    def delete_message(self, session_key, msg_no):
        '''
        쪽지 하나 삭제하기

        @type  session_key: string
        @param session_key: User Key
        @type  msg_no: integer
        @param msg_no: Message Number
        @rtype: string
        @return:
            1. 삭제 성공: True, 'OK'
            2. 삭제 실패:
                1. 메세지가 존재하지 않음: False, 'MSG_NOT_EXIST'
                2. 로그인되지 않은 사용자: False, 'NOT_LOGGED_IN'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        ret, user_info = self.login_manager.get_session(session_key)
        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info['username']).one()
        try:
            message_to_delete = session.query(model.Message).filter_by(id=msg_no).one()
        except InvalidRequestError:
            return False, 'MSG_NOT_EXIST'
        if message_to_delete.to_id == user.id:
            if message_to_delete.sent_deleted:
                session.delete(message_to_delete)
            else:
                message_to_delete.received_deleted = True
        elif message_to_delete.from_id == user.id:
            if message_to_delete.received_deleted:
                session.delete(message_to_delete)
            else:
                message_to_delete.sent_deleted = True
        else:
            return False, 'MSG_NOT_EXIST'
        session.commit()
        return True, 'OK'


# vim: set et ts=8 sw=4 sts=4
