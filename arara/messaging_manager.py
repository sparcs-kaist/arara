# -*- coding: utf-8 -*-
from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import or_, not_, and_

from libs import datetime2timestamp, filter_dict, smart_unicode

from arara import arara_manager
from arara import model
from arara_thrift.ttypes import *
from arara.util import require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_important

log_method_call = log_method_call_with_source('messaging_manager')
log_method_call_important = log_method_call_with_source_important('messaging_manager')

MESSAGE_WHITELIST = ['id', 'from_', 'to', 'from_nickname', 'to_nickname', 'message', 'sent_time', 'read_status', 'blacklisted']

class MessagingManager(arara_manager.ARAraManager):
    '''
    회원간 쪽지기능등을 담당하는 클래스
    '''

    def _get_dict(self, item, whitelist=None, blacklist_users=None):
        '''
        @type  item: model.Message
        @param item: dictionary 로 바꿀 객체 (여기서는 메시지)
        @type  whitelist: list<string>
        @param whitelist: dictionary 에 남아있을 필드의 목록
        @type  blacklist_users: list<string>
        @param blacklist_users: Blacklist 로 등록되어 있는 사용자의 목록
        @rtype: dict
        @return: item 에서 whitelist 에 있는 필드만 남기고 적절히 dictionary 로 변환한 결과물
        '''
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
        '''
        @type  raw_list: iterable(list, generator)<model.Message>
        @param raw_list: _get_dict 에 통과시키고 싶은 대상물의 모임
        @type  whitelist: list<string>
        @param whitelist: _get_dict 에 넘겨줄 whitelist
        @type  blacklist_users: list<string>
        @param blacklist_users: Blacklist 로 등록되어 있는 사용자의 목록
        @rtype: list<dict(whitelist filtered)>
        @return: _get_dict 를 통과시킨 raw_list 의 원소들의 list
        '''
        # TODO: Generator 화
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist, blacklist_users)
            return_list.append(Message(**filtered_dict))
        return return_list

    def _get_user_by_nickname(self, session, nickname):
        '''
        @type  session: model.Session
        @param session: 사용중인 SQLAlchemy Session
        @type  nickname: string
        @param nickname: 얻고자 하는 사용자의 nickname
        @rtype: model.User
        @return: 해당되는 사용자의 객체
        '''
        # TODO: member_manager 로 옮기기
        try:
            user = session.query(model.User).filter_by(nickname=smart_unicode(nickname)).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('nickname not found')
        return user

    @require_login
    @log_method_call
    def sent_list(self, session_key, page=1, page_length=20):
        '''
        보낸 쪽지 리스트 읽어오기

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  page: int
        @param page: Page Number
        @type  page_length: int
        @param page_length: Number of Messages to get in one page
        @rtype: ttypes.MessageList
        @return:
            1. 리스트 읽어오기 성공: MessageList
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: NotLoggedIn Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: ArticleManager 참고하여 싹 뜯어고치기
        # TODO: page 관련 정보 처리하는거 ArticleManager 에서 아예 util 로 옮기기
        ret_dict = {}
        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        sent_user = self.engine.member_manager._get_user(session, user_info.username)
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
                    )).order_by(model.Message.id.desc())[offset:last]
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
        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  page: int
        @param page: Page Number
        @type  page_length: int
        @param page_length: Number of Messages to get in one page
        @rtype: ttypes.MessageList
        @return:
            1. 리스트 읽어오기 성공: MessageList
            2. 리스트 읽어오기 실패:
                1. 로그인되지 않은 사용자: NotLoggedIn Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: ArticleManager 참고하여 싹 뜯어고치기
        # TODO: page 관련 정보 처리하는거 ArticleManager 에서 아예 util 로 옮기기

        ret_dict = {}
        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        to_user = self.engine.member_manager._get_user(session, user_info.username)
        blacklist_dict_list = self.engine.blacklist_manager.get_blacklist(session_key)
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
                    )).order_by(model.Message.id.desc())[offset:last]
        received_messages_dict_list = self._get_dict_list(received_messages, MESSAGE_WHITELIST, blacklist_users)
        ret_dict['hit'] = received_messages_dict_list
        ret_dict['last_page'] = last_page
        ret_dict['new_message_count'] = received_new_messages_count
        ret_dict['results'] = received_messages_count
        session.close()
        return MessageList(**ret_dict)

    @require_login
    @log_method_call
    def get_unread_message_count(self, session_key):
        '''
        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: int
        @return:
            받은 메시지 중 사용자가 아직 읽지 않은 메시지의 수
            오류시,
                1. 로그인되지 않은 사용자: NotLoggedIn Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: 위의 received_message_list 와 코드 중복을 해소한다
        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        to_user = self.engine.member_manager._get_user(session, user_info.username)
        received_unread_messages_count = session.query(model.Message).filter(
                and_(model.message_table.c.to_id==to_user.id,
                    model.message_table.c.read_status==u'N',
                    not_(model.message_table.c.received_deleted==True)
                    )).count()
        session.close()
        return received_unread_messages_count

    @require_login
    @log_method_call_important
    def send_message_by_username(self, session_key, to_username, msg):
        '''
        해당 하는 username을 갖는 사용자에게 쪽지를 전송하는 함수 

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  to_username: string
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

        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        to_user = self.engine.member_manager._get_user(session, to_username)
        from_user = self.engine.member_manager._get_user(session, user_info.username)
        from_user_ip = user_info.ip
        message = model.Message(from_user, from_user_ip, to_user, msg)
        try:
            session.add(message)
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
        @param session_key: 사용자 Login Session
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

        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        to_user = self._get_user_by_nickname(session, to_nickname)
        from_user = self.engine.member_manager._get_user(session, user_info.username)
        from_user_ip = user_info.ip
        message = model.Message(from_user, from_user_ip, to_user, msg)
        try:
            session.add(message)
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
        @param session_key: 사용자 Login Session
        @type  to_data: string / list
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
        # TODO: 위의 2개 함수와 이 함수의 차이점은?

        user_info = self.engine.login_manager.get_session(session_key)
        if type(to_data) == list:
            raise InvalidOperation('temporarily disabled')
        else:
            session = model.Session()
            to_user = self.engine.member_manager._get_user(session, to_data)
            from_user = self.engine.member_manager._get_user(session, user_info.username)
            from_user_ip = user_info.ip
            message = model.Message(from_user, from_user_ip, to_user, msg)
            try:
                session.add(message)
                session.commit()
            except InvalidRequestError:
                session.close()
                raise InternalError('database error')
            session.close()

    @require_login
    @log_method_call_important
    def read_received_message(self, session_key, msg_no):
        '''
        받은 쪽지 하나 읽어오기

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  msg_no: int
        @param msg_no: Message Number
        @rtype: ttypes.Message
        @return:
            1. 읽어오기 성공: Message Dictionary
            2. 읽어오기 실패:
                1. 메세지가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: 쿼리 부분 분리하여 좀더 함수 조립식으로 만들기
        
        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        to_user = self.engine.member_manager._get_user(session, user_info.username)
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
        @param session_key: 사용자 Login Session
        @type  msg_no: int
        @param msg_no: Message Number
        @rtype: dictionary
        @return:
            1. 읽어오기 성공: Message
            2. 읽어오기 실패:
                1. 메세지가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: 쿼리 부분 분리하여 좀더 함수 조립식으로 만들기
        
        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        from_user = self.engine.member_manager._get_user(session, user_info.username)
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
        @param session_key: 사용자 Login Sesion
        @type  msg_no: int
        @param msg_no: Message Number
        @rtype: void
        @return:
            1. 삭제 성공: void
            2. 삭제 실패:
                1. 메세지가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: 아래 로지컬 패쓰 좀 개선하기

        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        user = self.engine.member_manager._get_user(session, user_info.username)
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
        @param session_key: 사용자 Login Session
        @type  msg_no: int
        @param msg_no: Message Number
        @rtype: void
        @return:
            1. 삭제 성공: void
            2. 삭제 실패:
                1. 메세지가 존재하지 않음: InvalidOperation Exception
                2. 로그인되지 않은 사용자: NotLoggedIn Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: 위 함수와 왜 분리되어 있는지 알 수 없다.

        user_info = self.engine.login_manager.get_session(session_key)
        session = model.Session()
        user = self.engine.member_manager._get_user(session, user_info.username)
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

    __public__ = [
            sent_list,
            receive_list,
            get_unread_message_count,
            send_message_by_username,
            send_message_by_nickname,
            send_message,
            read_received_message,
            read_sent_message,
            delete_received_message,
            delete_sent_message]
