# -*- coding: utf-8 -*-
from sqlalchemy.exceptions import InvalidRequestError, IntegrityError
from arara import model
from arara.util import filter_dict, require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_important

from arara_thrift.ttypes import *
from arara.server import get_server

log_method_call = log_method_call_with_source('board_manager')
log_method_call_important = log_method_call_with_source_important('board_manager')

BOARD_MANAGER_WHITELIST = ('board_name', 'board_description', 'read_only')

class BoardManager(object):
    '''
    보드 추가 삭제 및 관리 관련 클래스
    '''

    def __init__(self):
        pass

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
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
    @log_method_call_important
    def add_board(self, session_key, board_name, board_description):
        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info.username).one()
        if not user.is_sysop:
            session.close()
            raise InvalidOperation('no permission')
        board_to_add = model.Board(board_name, board_description)
        try:
            session.save(board_to_add)
            session.commit()
            session.close()
            return
        except IntegrityError:
            session.rollback()
            session.close()
            raise InvalidOperation('already added')

    @log_method_call
    def get_board(self, board_name):
        session = model.Session()
        try:
            board_to_get = session.query(model.Board).filter_by(board_name=board_name, deleted=False).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('board does not exist')
        board_dict = self._get_dict(board_to_get, BOARD_MANAGER_WHITELIST)
        session.close()
        return Board(**board_dict)

    @log_method_call
    def get_board_list(self):
        session = model.Session()
        board_to_get = session.query(model.Board).filter_by(deleted=False).all()
        board_dict_list = self._get_dict_list(board_to_get, BOARD_MANAGER_WHITELIST)
        session.close()
        return [Board(**d) for d in board_dict_list]

    @require_login
    @log_method_call_important
    def add_read_only_board(self, session_key, board_name):
        '''
        보드를 읽기 전용으로 변경해주는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @rtype: boolean, string 
        @return:
            1. 읽기전용 성공: True, 'OK' 
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 이미 읽기전용인 보드의 경우: False, 'ALEARDY_READ_ONLY_BOARD'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info.username).one()
        if not user.is_sysop:
            session.close()
            raise InvalidOperation('no permission')
        try:
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            if board.read_only:
                session.close()
                raise InvalidOperation('aleardy read only board')
            board.read_only = True
            session.commit()
            session.close()
            return
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('board does not exist')


    @require_login
    @log_method_call_important
    def return_read_only_board(self, session_key, board_name):
        '''
        보드를 읽기 전용에서 다시 쓰기/읽기 가능 보드로 변경해주는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @rtype: boolean, string 
        @return:
            1. 성공: True, 'OK' 
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 이미 읽기전용가 아닌경우 보드의 경우: False, 'not read only board'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info.username).one()
        if not user.is_sysop:
            session.close()
            raise InvalidOperation('no permission')
        try:
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            if not board.read_only:
                session.close()
                raise InvalidOperation('not read only board')
            board.read_only = False
            session.commit()
            session.close()
            return
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('board does not exist')
        

    @require_login
    @log_method_call_important
    def delete_board(self, session_key, board_name):
        user_info = get_server().login_manager.get_session(session_key)
        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info.username).one()
        try:
            board = session.query(model.Board).filter_by(board_name=board_name).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('board does not exist')
        if not user.is_sysop:
            session.close()
            raise InvalidOperation('no permission')
        board.deleted = True
        session.commit()
        session.close()
        return
