# -*- coding: utf-8 -*-

import random
from sqlalchemy.exceptions import InvalidRequestError
from arara import arara_manager
from arara import model
from arara_thrift.ttypes import *
from arara.util import require_login, filter_dict, is_keys_in_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import timestamp2datetime, datetime2timestamp

log_method_call = log_method_call_with_source('notice_manager')
log_method_call_important = log_method_call_with_source_important('notice_manager')

NOTICE_QUERY_WHITELIST = ('id', 'content', 'issued_date', 'due_date', 'valid', 'weight')
NOTICE_PUBLIC_WHITELIST= ('id', 'content', 'issued_date', 'due_date', 'valid', 'weight')
NOTICE_ADD_WHITELIST = ('content','due_date','weight')

class NoticeManager(arara_manager.ARAraManager):
    '''
    배너 및 환영 페이지 처리 관련 클래스
    '''

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__

        if item_dict.has_key('issued_date'):
            item_dict['issued_date'] = datetime2timestamp(item_dict['issued_date'])
        if item_dict.has_key('due_date'):
            item_dict['due_date'] = datetime2timestamp(item_dict['due_date'])

        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(Notice(**filtered_dict))
        return return_list

    @log_method_call
    def get_banner(self):
        '''
        배너를 가져오는 함수

        >>> notice.get_banner()
        '<html> .... '

        @rtype: string
        @return:
            1. 배너가 있을 때: 랜덤하게 선택된 배너(html)
            2. 배너가 없을 때: InvalidOperation Exception
        '''
        session = model.Session()
        available_banner = session.query(model.Banner).filter_by(valid=True).all()
        available_banner_dict_list = self._get_dict_list(available_banner, NOTICE_PUBLIC_WHITELIST)
        if available_banner_dict_list:
            weight_banner = []
            for index in range(len(available_banner_dict_list)):
                for weight in range(available_banner_dict_list[index].weight):
                    weight_banner.append(index)
            n = random.choice(weight_banner)
            session.close()
            return available_banner_dict_list[n].content
        else:
            session.close()
            raise InvalidOperation('no banner')

    @log_method_call
    def get_welcome(self):
        '''
        welcome 가져오는 함수

        >>> notice.get_welcome()
        '<html> .... '

        @rtype: string
        @return:
            1. welcome 있을 때: 랜덤하게 선택된 welcome(html)
            2. welcome 없을 때: InvalidOperation Exception
        '''
        session = model.Session()
        available_welcome= session.query(model.Welcome).filter_by(valid=True).all()
        available_welcome_dict_list = self._get_dict_list(available_welcome, NOTICE_PUBLIC_WHITELIST)
        if available_welcome_dict_list:
            weight_welcome = []
            for index in range(len(available_welcome_dict_list)):
                for weight in range(available_welcome_dict_list[index].weight):
                    weight_welcome.append(index)
            n = random.choice(weight_welcome)
            session.close()
            return available_welcome_dict_list[n].content
        else:
            session.close()
            raise InvalidOperation('no welcome')

    @require_login
    @log_method_call_important
    def list_banner(self, session_key):
        '''
        관리자용 banner 페이지 목록을 가져오는 함수

        @type  session_key: string
        @param session_key: Session Key (시삽이어야 함)
        @rtype: list
        @return:
            1. banner 페이지가 있을 때: banner 페이지들의 목록
            2. banner 페이지가 없을 때: [] (빈 스트링)
                1. 데이터베이스 오류: InternalError Exception
            3. 시삽이 아닐 때: InvalidOperation Exception
        '''
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('not sysop')

        session = model.Session()
        banner = session.query(model.Banner).all()
        banner_dict_list = self._get_dict_list(banner, NOTICE_PUBLIC_WHITELIST)

        return banner_dict_list

    @require_login
    @log_method_call_important
    def list_welcome(self, session_key):
        '''
        관리자용 welcome 페이지 목록을 가져오는 함수

        >>> notice.list_welcome(SYSOP_session_key)
        [{'no': 32, 'content': '신입회원을 모집합니다','availability': 'True'}, {'no': 33', content': '환영합니다','availability': 'False'}

        @rtype: list
        @return:
            1. welcome 페이지가 있을 때: True, welcome 페이지들의 목록(text)
            2. welcome 페이지가 없을 때: 
                1. welcome 없을때   : False, 'NO_WELCOME'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
            3. 시삽이 아닐 때: False, 'NOT_SYSOP'
        '''
        
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('not sysop')
        session = model.Session()
        welcome= session.query(model.Welcome).all()
        welcome_dict_list = self._get_dict_list(welcome, NOTICE_PUBLIC_WHITELIST)

        if welcome_dict_list:
            session.close()
            return welcome_dict_list
        else:    
            session.close()
            raise InvalidOperation('no welcome')
        

    @require_login    
    @log_method_call_important
    def add_banner(self, session_key, notice_reg_dic):
        '''
        관리자용 배너 추가 함수
        이 아래의 doctest 는 작동하지 않으니 무시할 것.
       
        >>> notice_reg_dic = { 'content':'hahahah', 'due_date':'2008,7,14', 'weight':'1' }
        >>> notice.add_banner(SYSOP_session_key, WrittenNotice(**notice_reg_dic))
        >>> notice.add_banner(user_session_key, notice_reg_dic)
        Traceback (most recent calls top):
            ...
        InvalidOperation
        
        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  notice_reg_dic: ttypes.WrittenNotice 
        @param notice_reg_dic: Notice Dictionary
        @rtype: int
        @return:
            1. 배너 페이지 추가에 성공하였을 때: 추가된 배너의 id
            2. 배너 페이지 추가에 실패하였을 때:
                1. 시삽이 아닐 때: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        notice_reg_dic = notice_reg_dic.__dict__
        notice_reg_dic['due_date'] = timestamp2datetime(
                notice_reg_dic['due_date'])

        if not is_keys_in_dict(notice_reg_dic, NOTICE_ADD_WHITELIST):
            raise InvalidOperation('wrong dictionary')

        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('not sysop')

        session = model.Session()
        try:
            # Register welcome to db
            banner = model.Banner(**notice_reg_dic)
            session.add(banner)
            session.commit()
            banner_id = banner.id
            session.close()
            return banner_id
        except Exception, e:
            session.rollback()
            session.close()
            raise InternalError('database error')

    @require_login    
    @log_method_call_important
    def add_welcome(self, session_key, notice_reg_dic):
        '''
        관리자용 welcome 추가 함수

        >>> notice_reg_dic = { 'content':'hahahah', 'due_date':'2008,7,14', 'weight':'1' }
        >>> notice.add_welcome(SYSOP_session_key, notice_reg_dic)
        >>> notice.add_welcome(user_session_key, notice_reg_dic)
        Traceback (most recent calls top):
            ...
        InvalidOperation
        
        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  notice_reg_dic: dictionary
        @param notice_reg_dic: Notice Dictionary
        @rtype: void
        @return:
            1. welcome 페이지 추가에 성공하였을 때: void
            2. welcome 페이지 추가에 실패하였을 때:
                1. 시삽이 아닐 때: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''

        notice_reg_dic = notice_reg_dic.__dict__

        notice_reg_dic['due_date'] = timestamp2datetime(
                notice_reg_dic['due_date'])

        if not is_keys_in_dict(notice_reg_dic, NOTICE_ADD_WHITELIST):
            raise InvalidOperation('wrong dictionary')

        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('not sysop')

        session = model.Session()
        try:
            # Register welcome to db
            welcome= model.Welcome(**notice_reg_dic)
            session.save(welcome)
            session.commit()
            session.close()
            return
        except Exception, e:
            session.rollback()
            session.close()
            raise InternalError('database error')

    @require_login    
    @log_method_call_important
    def modify_banner_validity(self, session_key, id, valid):
        '''
        배너의 valid 필드만 바꿔주는 함수
       
        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  id: int
        @param id: 바꾸고자 하는 banner 의 id
        @type  valid: bool
        @param valid: 설정하고자 하는 해당 banner 의 validity
        @rtype: void
        @return:
            1. 배너 validity 설정 변경에 성공하였을 때 : void
            2. 실패하면?
                1. 시삽이 아닐 때: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('not sysop')

        session = model.Session()
        try:
            # 배너를 하나 고른다.
            chosen_banner = session.query(model.Banner).filter_by(id=id).one()
            if chosen_banner:
                if chosen_banner.valid != valid:
                    chosen_banner.valid = valid
                    session.commit()
                session.close()
            else:
                session.close()
                raise InvalidOperation('not existing banner')

        except Exception, e:
            session.close()
            raise InternalError('database error')

    @require_login 
    @log_method_call_important
    def remove_banner(self, session_key, id):
        '''
        관리자용 배너 제거 함수

        >>> notice.remove_banner(SYSOP_session_key, 33)
        >>> notice.remove_banner(user_session_key, 33)
        Traceback (most recent call top):
            ...
        InvalidOperation
        >>> notice.remove_banner(SYSOP_session_key, -1)
        Traceback (most recent call top):
            ...
        InvalidOperation

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  id: i32
        @param id: 제거하고자 하는 banner 의 id
        @rtype: void
        @return:
            1. 배너 제거에 성공하였을 때: void
            2. 배너 제거에 실패하였을 때:
                1. 시삽이 아닐 때: InvalidOperation Exception
                2. 존재하지 않는 배너번호일 때: InvalidOperation Exception 
                3. 데이터베이스 오류: InternalError Exception
        '''
        
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('not sysop')
        try:
            session = model.Session()
            invalid_banner= session.query(model.Banner).filter_by(id = id).one()
            if invalid_banner:
                invalid_banner.valid = 'False'
                session.close()
                return
            else:
                session.close()
                raise InvalidOperation('not exist welcome')
        except Exception:
            session.close()
            raise InternalError('database error')
    
    @require_login 
    @log_method_call_important
    def remove_welcome(self, session_key, id):
        '''
        관리자용 welcome 제거 함수

        >>> notice.remove_welcome(SYSOP_session_key, 33)
        >>> notice.remove_welcome(user_session_key, 33)
        Traceback (most recent call top):
            ...
        InvalidOperation
        >>> notice.remove_welcome(SYSOP_session_key, -1)
        Traceback (most recent call top):
            ...
        InvalidOperation

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  id: i32
        @param id: 제거하고자 하는 banner 의 id
        @rtype: void
        @return:
            1. welcome 제거에 성공하였을 때: void
            2. welcome 제거에 실패하였을 때:
                1. 시삽이 아닐 때: InvalidOperation('not sysop')
                2. 존재하지 않는 welcome번호일 때: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('not sysop')
        try:
            session = model.Session()
            invalid_welcome= session.query(model.Welcome).filter_by(id = id).one()
            if invalid_welcome:
                invalid_welcome.valid = 'False'
                session.close()
                return
            else:
                session.close()
                raise InvalidOperation('not exist welcome')
        except:
            session.close()
            raise InternalError('database error')

    __public__ = [
            get_banner,
            get_welcome,
            list_banner,
            list_welcome,
            add_banner,
            add_welcome,
            modify_banner_validity,
            remove_banner,
            remove_welcome]
