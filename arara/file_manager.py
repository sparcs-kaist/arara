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

    @require_login
    def save_file(self, session_key, filename, filepath, user, board, article):
        '''
        article작성시 파일을 저장하는 함수
        외부에서 사용하는 함수가 아닌 내부적으로 사용되는 함수
        
        @type  session_key: string
        @param session_key: User Key
        @type  filename: string
        @param filename: File Name
        @type  filepath: string
        @param filepath: File Path
        @type  user: object
        @param user: User Object
        @type  board: object
        @param board: Board Object 
        @type  article: object
        @param article: Article Object 
        @rtype: boolean, string
        @return:
            1. 저장 성공: True, 'OK' 
            2. 저장 실패:
                1. path에 파일이 없는 경우: False, 'THERE IS NO FILE'
                2. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                3. 위험한 파일: False, 'DANGER_FILE_DETECTED'
                4. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        #그 경로의 파일이 있는지 확인
        #업로드 된 파일이 안전한 파일인지 확인?!!

        DANGER_FILE = ('php', 'asp', 'php3', 'php4', 'htaccess', 'js')
        file_ext = filename.split('.',1)[-1]
        if file_ext in DANGER_FILE:
            return False, 'DANGER_FILE_DETECTED'
        
        ret = Ture
        #위의 두 경우를 만족 시켰을 경우 true 아니면 false 지금은 일단 true로 해서 코딩함...
        if ret:
            session = model.Session()
            file = model.File(filename, filepath, user, board, article)
            session.save(file)
            session.commit()
            return True, 'OK'
        else: 
            return False, 'Error' 

    @require_login
    def download_file(self, session_key):
        '''
        파일을 다운로드하는 함수
        '''

        pass

    @require_login
    def delete_file(self, session_key);
        '''
        파일을 지우는 함수
        '''
        pass


