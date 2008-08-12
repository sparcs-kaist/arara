#!/usr/bin/python
# -*- coding: utf-8 -*-

import md5 as hashlib

from arara.util import require_login
from arara import model

from sqlalchemy import and_, or_, not_
from sqlalchemy.exceptions import InvalidRequestError

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
        article작성시 파일을 저장할 장소와 저장할 파일명를 리턴해주는 함수
        
        @type  session_key: string
        @param session_key: User Key
        @type  article_id: integer
        @param article_id: Article Number
        @type  filename: string
        @param filename: File Name
        @rtype: boolean, string, string
        @return:
            1. 저장 성공: True, 'garbages/2008/8/7', 'adfasdfasdfadf' 
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
        filepath_to_save = u''+str(article.board.board_name) + '/' +str(article.date.year) + '/' + str(article.date.month) + '/' + str(article.date.day)
        try:
            ghost_filename = u''+hashlib.md5(str(filename) + str(article.author.id) + str(article.board.id) + str(article.id)).hexdigest()
            file = model.File(filename, ghost_filename, filepath_to_save, article.author, article.board, article)
            session.save(file)
            session.commit()
            session.close()
            return True, filepath_to_save, ghost_filename 
        except Exception: 
            session.close()
            return False, 'DATABASE_ERROR' 

    @require_login
    def download_file(self, session_key, article_id, filename):
        '''
        article의 파일을 다운로드 할때 실제로 파일이 저장된 장소와 저장된 파일명을 리턴해주는 함수 
        
        @type  session_key: string
        @param session_key: User Key
        @type  article_id: Integer 
        @param article_id: Article Number 
        @type  filename: string
        @param filename: File Name
        @rtype: boolean, string
        @return:
            1. 경로 찾기 성공: True, 'garbages/2008/8/7', 'asdfasdfasdfasdf' 
            2. 경로 찾기 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        session = model.Session()
        try:
            article = session.query(model.Article).filter_by(id = article_id).one()
        except InvalidRequestError:
            session.close()
            return False, 'ARTICLE_NOT_EXIST'
        try:
            file = session.query(model.File).filter(
                    and_(model.file_table.c.filename == filename,
                    model.file_table.c.user_id == article.author.id,
                    model.file_table.c.board_id == article.board.id,
                    model.file_table.c.article_id == article.id, 
                    model.file_table.c.deleted == False
                    )).one()
        except InvalidRequestError:
            session.close()
            return False, 'FILE_NOT_FOUND'
        download_path = file.filepath
        ghost_filename = file.saved_filename
        session.commit()
        session.close()
        return True, download_path, ghost_filename

    @require_login
    def delete_file(self, session_key, article_id, filename):
        '''
        지울 파일이 저장된 장소와 저장된 파일명을 리턴해주는 함수
        
        @type  session_key: string
        @param session_key: User Key
        @type  article_id: Integer 
        @param article_id: Article Number 
        @type  filename: string
        @param filename: File Name
        @rtype: boolean, string
        @return:
            1. 성공: True, 'garbages/2008/8/7' 
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        #ret, filepath_to_delete= self.download_file(session_key, article_id, filename)
        #download_file함수와 유사하다.. 똑같은 코드가 많다.. 먼가 비효율적이다.. 나중에 하나로 좀 해보자.. 일단 지금은 급하니까.. 복사해놓고...
        session = model.Session()
        try:
            article = session.query(model.Article).filter_by(id = article_id).one()
        except InvalidRequestError:
            session.close()
            return False, 'ARTICLE_NOT_EXIST'
        try:
            file = session.query(model.File).filter(
                    and_(model.file_table.c.filename == filename,
                    model.file_table.c.user_id == article.author.id,
                    model.file_table.c.board_id == article.board.id,
                    model.file_table.c.article_id == article.id,
                    model.file_table.c.deleted == False,
                    )).one()
        except InvalidRequestError:
            session.close()
            return False, 'FILE_NOT_FOUND'
        file.deleted = True
        download_path = file.filepath
        ghost_filename = file.saved_filename
        session.commit()
        session.close()
        return True, download_path, ghost_filename

