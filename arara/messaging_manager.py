# -*- coding: utf-8 -*-
import datetime
import time

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import or_, not_, and_
from arara import model
from arara_thrift.ttypes import *
from arara.util import require_login, filter_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import datetime2timestamp
from arara.server import get_server

log_method_call = log_method_call_with_source('messaging_manager')
log_method_call_important = log_method_call_with_source_important('messaging_manager')

MESSAGE_WHITELIST = ['id', 'from_', 'to', 'from_nickname', 'to_nickname', 'message', 'sent_time', 'read_status', 'blacklisted']

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

    def _get_dict(self, item, whitelist=None, blacklist_users=None):
        item_dict = item.__dict__
        if item_dict.has_key('from_id'):
            item_dict['from_'] = item.from_user.username
            item_dict['from_nickname'] = item.from_user.nickname
            del item_dict['from_id']
        if item_dict.has_key('to_id'):
            item_dict['to'] = item.to_user.username
            item_dict['to_nickname'] = item.to_user.nickname
            del item_dict['to_id']
        if item_dict.has_key('sent_time'):
            item_dict['sent_time']=datetime2timestamp(
                    item_dict['sent_time'])
        if blacklist_users:
            if item_dict.has_key('from_'):
                if item_dict['from_'] in blacklist_users:
                    item_dict['blacklisted'] = True
                else:
                    item_dict['blacklisted'] = False
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None, blacklist_users=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist, blacklist_users)
            return_list.append(Message(**filtered_dict))
        return return_list

    def _get_user(self, session, username):
        try:
            user = session.query(model.User).filter_by(username=username).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('username not found')
        return user

    def _get_user_by_nickname(self, session, nickname):
        try:
            user = session.query(model.User).filter_by(nickname=nickname).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('username not found')
        return user

    @require_login
    @log_method_call
    def sent_list(self, session_key, page=1, page_length=20):
        '''
        보낸 쪽지 리스트 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @type  page: integer
        @param page: Page Number
        @type  page_length: integer
        @param page_length: Number of Messages to get in one page
        @rtype: MessageList
        @return:
            1. 리스트 읽어오기 성공: MessageList
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: NotLoggedIn Exception
                2. 데이터베이스 오류: InternalError Exception
        '''

        ret_dict = {}
        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        sent_user = self._get_user(session, user_info.username)
        sent_messages_count = session.query(model.Message).filter(
                and_(model.message_table.c.from_id==sent_user.id,
                    not_(model.message_table.c.sent_deleted==True)
                    )).count()
        page = int(page)
        last_page = int(sent_messages_count / page_length)
        if sent_messages_count % page_length != 0:
            last_page += 1
        elif sent_messages_count == 0:
            last_page += 1
        if page > last_page:
            session.close()
            raise InvalidOperation('wrong pagenum')
        offset = page_length * (page - 1)
        last = offset + page_length
        sent_messages = session.query(model.Message).filter(
                and_(model.message_table.c.from_id==sent_user.id,
                    not_(model.message_table.c.sent_deleted==True)
                    ))[offset:last].order_by(model.Message.id.desc()).all()
        sent_messages_dict_list = self._get_dict_list(sent_messages, MESSAGE_WHITELIST)
        ret_dict['hit'] = sent_messages_dict_list
        ret_dict['last_page'] = last_page
        ret_dict['results'] = sent_messages_count
        session.close()
        return MessageList(**ret_dict)


    @require_login
    @log_method_call
    def receive_list(self, session_key, page=1, page_length=20):
        '''
        받은 쪽지 리스트 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @type  page: integer
        @param page: Page Number
        @type  page_langth: integer
        @param page_length: Number of Messages to get in one page
        @rtype: MessageList
        @return:
            1. 리스트 읽어오기 성공: MessageList
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: NotLoggedIn Exception
                2. 데이터베이스 오류: InternalError Exception
        '''

        ret_dict = {}
        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        to_user = self._get_user(session, user_info.username)
        blacklist_dict_list = get_server().blacklist_manager.list_(session_key)
        blacklist_users = set()
        for blacklist_item in blacklist_dict_list:
            if blacklist_item.block_message:
                blacklist_users.add(blacklist_item.blacklisted_user_username)
        received_messages_count = session.query(model.Message).filter(
                and_(model.message_table.c.to_id==to_user.id,
                    not_(model.message_table.c.received_deleted==True)
                    )).count()
        received_new_messages_count = session.query(model.Message).filter(
                and_(model.message_table.c.to_id==to_user.id,
                    model.message_table.c.read_status==u'N',
                    not_(model.message_table.c.received_deleted==True)
                    )).count()
        last_page = int(received_messages_count / page_length)
        page = int(page)
        if received_messages_count % page_length != 0:
            last_page += 1
        elif received_messages_count == 0:
            last_page += 1
        if page > last_page:
            session.close()
            raise InvalidOperation('wrong pagenum')
        offset = page_length * (page - 1)
        last = offset + page_length
        received_messages = session.query(model.Message).filter(
                and_(model.message_table.c.to_id==to_user.id, 
                    not_(model.message_table.c.received_deleted==True)
                    )).order_by(model.Message.id.desc())[offset:last].all()
        received_messages_dict_list = self._get_dict_list(received_messages, MESSAGE_WHITELIST, blacklist_users)
        ret_dict['hit'] = received_messages_dict_list
        ret_dict['last_page'] = last_page
        ret_dict['new_message_count'] = received_new_messages_count
        ret_dict['results'] = received_messages_count
        session.close()
        return MessageList(**ret_dict)

    @require_login
    @log_method_call_important
    def send_message_by_username(self, session_key, to_username, msg):
        '''
        해당 하는 username을 갖는 사용자에게 쪽지를 전송하는 함수 

        @type  session_key: string
        @param session_key: User Key
        @type  to_username: string, list
        @param to_username: Destination username
        @type  msg: string
        @param msg: Message string
        @rtype: void
        @return:
            1. 메세지 전송 성공: void
            2. 메세지 전송 실패:
                1. 보낼 아이디가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''

        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        to_user = self._get_user(session, to_username)
        from_user = self._get_user(session, user_info.username)
        from_user_ip = user_info.ip
        message = model.Message(from_user, from_user_ip, to_user, msg)
        try:
            session.save(message)
            session.commit()
        except InvalidRequestError:
            session.close()
            raise InternalError('database error')
        session.close()

    @require_login
    @log_method_call_important
    def send_message_by_nickname(self, session_key, to_nickname, msg):
        '''
        해당 하는 nickname을 갖는 사용자에게 쪽지를 전송하는 함수 

        @type  session_key: string
        @param session_key: User Key
        @type  to_nickname: string
        @param to_nickname: Destination nickname
        @type  msg: string
        @param msg: Message string
        @rtype: void
        @return:
            1. 메세지 전송 성공: void
            2. 메세지 전송 실패:
                1. 보낼 아이디가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''

        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        to_user = self._get_user_by_nickname(session, to_nickname)
        from_user = self._get_user(session, user_info.username)
        from_user_ip = user_info.ip
        message = model.Message(from_user, from_user_ip, to_user, msg)
        try:
            session.save(message)
            session.commit()
        except InvalidRequestError:
            session.close()
            raise InternalError('database error')
        session.close()

    @require_login
    @log_method_call_important
    def send_message(self, session_key, to_data, msg):
        '''
        쪽지 전송하기

        보내는 사람 항목인 to에는 한 명의 아이디 혹은 아이디의 리스트를 보낼 수 있음

        현재  스팸 쪽지등의 문제로 인하여 아이디를 리스트로 보낼경우 작동하지 않도록 되어있음. 
        @type  session_key: string
        @param session_key: User Key
        @type  to_data: string, list
        @param to_data: Destination username
        @type  msg: string
        @param msg: Message string
        @rtype: void
        @return:
            1. 메세지 전송 성공: void
            2. 메세지 전송 실패:
                1. 보낼 아이디가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception 
        '''

        user_info = get_server().login_manager.get_session(session_key)
        if type(to_data) == list:
            raise InvalidOperation('temporarily disabled')
            #ret = []
            #for to in to_data: 
            #    if get_server().member_manager.is_registered(to):
            #        session = model.Session()
            #        from_user = session.query(model.User).filter_by(username=user_info.username).one()
            #        from_user_ip = user_info.ip
            #        to_user = session.query(model.User).filter_by(username=to).one()
            #        message = model.Message(from_user, from_user_ip, to_user, msg)
            #        try:
            #            session.save(message)
            #            session.commit()
            #            ret.append('OK')
            #        except InvalidRequestError:
            #            return False, "DATABASE_ERROR"
            #    else:
            #        ret.append('USER_NOT_EXIST')
            #return True, ret
        else:
            session = model.Session()
            to_user = self._get_user(session, to_data)
            from_user = self._get_user(session, user_info.username)
            from_user_ip = user_info.ip
            message = model.Message(from_user, from_user_ip, to_user, msg)
            try:
                session.save(message)
                session.commit()
            except InvalidRequestError:
                session.close()
                raise InternalError('database error')
            session.close()

    @require_login
    @log_method_call_important
    def read_received_message(self, session_key, msg_no):
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
                1. 메세지가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        
        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        to_user = self._get_user(session, user_info.username)
        try:
            message = session.query(model.Message).filter(and_(model.message_table.c.to_id==to_user.id, model.message_table.c.id==msg_no, not_(model.message_table.c.received_deleted==True))).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('message not exist')
        message_dict = self._get_dict(message, MESSAGE_WHITELIST)
        message.read_status = u'R'
        session.commit()
        session.close()
        return Message(**message_dict)

    @require_login
    @log_method_call_important
    def read_sent_message(self, session_key, msg_no):
        '''
        쪽지 하나 읽어오기

        @type  session_key: string
        @param session_key: User Key
        @type  msg_no: integer
        @param msg_no: Message Number
        @rtype: dictionary
        @return:
            1. 읽어오기 성공: Message
            2. 읽어오기 실패:
                1. 메세지가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        
        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        from_user = self._get_user(session, user_info.username)
        try:
            message = session.query(model.Message).filter(and_(model.message_table.c.from_id==from_user.id, model.message_table.c.id==msg_no, not_(model.message_table.c.sent_deleted==True))).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('message not exist')
        message_dict = self._get_dict(message, MESSAGE_WHITELIST)
        message.read_status = u'R'
        session.commit()
        session.close()
        return Message(**message_dict)

    @require_login
    @log_method_call_important
    def delete_received_message(self, session_key, msg_no):
        '''
        받은 쪽지 하나 삭제하기

        @type  session_key: string
        @param session_key: User Key
        @type  msg_no: integer
        @param msg_no: Message Number
        @rtype: void
        @return:
            1. 삭제 성공: void
            2. 삭제 실패:
                1. 메세지가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''

        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        user = self._get_user(session, user_info.username)
        try:
            message_to_delete = session.query(model.Message).filter_by(id=msg_no).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('message not exist')
        if message_to_delete.to_id == user.id:
            if message_to_delete.sent_deleted:
                session.delete(message_to_delete)
                session.commit()
                session.close()
                return
            else:
                message_to_delete.received_deleted = True
                session.commit()
                session.close()
                return
        session.close()
        raise InvalidOperation('message not exist')

    @require_login
    @log_method_call_important
    def delete_sent_message(self, session_key, msg_no):
        '''
        보낸 쪽지 하나 삭제하기

        @type  session_key: string
        @param session_key: User Key
        @type  msg_no: integer
        @param msg_no: Message Number
        @rtype: void
        @return:
            1. 삭제 성공: void
            2. 삭제 실패:
                1. 메세지가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''

        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        user = self._get_user(session, user_info.username)
        try:
            message_to_delete = session.query(model.Message).filter_by(id=msg_no).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('message not exist')
        if message_to_delete.from_id == user.id:
            if message_to_delete.received_deleted:
                session.delete(message_to_delete)
                session.commit()
                session.close()
                return
            else:
                message_to_delete.sent_deleted = True
                session.commit()
                session.close()
                return
        session.close()
        raise InvalidOperation('message not exist')
# vim: set et ts=8 sw=4 sts=4
