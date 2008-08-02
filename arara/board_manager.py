# -*- coding: utf-8 -*-
from arara.util import require_login, filter_dict
from arara import model
from sqlalchemy.exceptions import InvalidRequestError, IntegrityError

BOARD_MANAGER_WHITELIST = ('board_name', 'board_description')

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
        session = model.Session()
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
    def add_board(self, session_key, board_name, board_description):
        ret, user_info = self.login_manager.get_session(session_key)
        session = model.Session()
        user = session.query(model.User).filter_by(username=user_info['username']).one()
        if not user.is_sysop:
            return False, 'NO_PERMISSION'
        board_to_add = model.Board(board_name, board_description)
        try:
            session.save(board_to_add)
            session.commit()
            return True, 'OK'
        except IntegrityError:
            session.rollback()
            return False, 'ALREADY_ADDED'

    def get_board(self, board_name):
        session = model.Session()
        try:
            board_to_get = session.query(model.Board).filter_by(board_name=board_name).one()
        except InvalidRequestError:
            return False, 'BOARD_NOT_EXIST'
        board_dict = self._get_dict(board_to_get, BOARD_MANAGER_WHITELIST)
        return True, board_dict

    def get_board_list(self):
        session = model.Session()
        try:
            board_to_get = session.query(model.Board).all()
        except InvalidRequestError:
            return False, 'NO_BOARD_EXIST'
        board_dict_list = self._get_dict_list(board_to_get, BOARD_MANAGER_WHITELIST)
        return True, board_dict_list

    @require_login
    def delete_board(self, session_key, board_name):
        session = model.Session()
        try:
            board = session.query(model.Board).filter_by(board_name=board_name).one()
        except InvalidRequestError:
            return False, 'BOARD_NOT_EXIST'
        if not user.is_sysop:
            return False, 'NO_PERMISSION'
        session.delete(board)
        session.commit()
        pass

