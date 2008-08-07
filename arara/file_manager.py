#!/usr/bin/python
# -*- coding: utf-8 -*-

from arara.util import require_login
from arara import model

class FileManager(object):
    '''
    파일 처리 관련 클래스
    '''
    
    def __init__(self):
        pass

    def _is_board_exist(self, board_name):
        ret, _ = self.board_manager.get_board(board_name)
        if ret:
            return True, 'OK'
        else:
            return False, 'BOARD_NOT_EXIST'

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    @require_login
    def save_file(self, session_key, article_id, filename):
        '''
        article작성시 파일을 저장할 장소를 리턴해주는 함수
        
        @type  session_key: string
        @param session_key: User Key
        @type  article_id: integer
        @param article_id: Article Number
        @type  filename: string
        @param filename: File Name
        @rtype: boolean, string
        @return:
            1. 저장 성공: True, 'garbages/2008/8/7' 
            2. 저장 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 위험한 파일: False, 'DANGER_FILE_DETECTED'
                3. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        #그 경로의 파일이 있다고 가정하고 저장

        DANGER_FILE = ('php', 'asp', 'php3', 'php4', 'htaccess', 'js')
        file_ext = filename.split('.',1)[-1]
        if file_ext in DANGER_FILE:
            return False, 'DANGER_FILE_DETECTED'
        
        session = model.Session()
        article = session.query(model.Article).filter_by(id=article_id).one()
        filepath_to_save = str(article.board.board_name) + '/' +str(article.date.year) + '/' + str(article.date.month) + '/' + str(article.date.day)
        try:
            file = model.File(filename, filepath_to_save, article.author, article.board, article)
            session.save(file)
            session.commit()
            return True, filepath_to_save 
        except Exception: 
            raise
            return False, 'DATABASE_ERROR' 

    @require_login
    def download_file(self, session_key, article, filename):
        '''
        article의 파일을 다운로드 할때 실제로 파일이 저장된 장소를 리턴해주는 함수 
        
        @type  session_key: string
        @param session_key: User Key
        @type  article: object
        @param article: Article Object 
        @type  filename: string
        @param filename: File Name
        @rtype: boolean, string
        @return:
            1. 저장 성공: True, 'garbages/2008/8/7' 
            2. 저장 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

    @require_login
    def delete_file(self, session_key):
        '''
        파일을 지우는 함수
        '''
        pass


