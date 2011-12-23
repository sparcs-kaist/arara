#-*- coding: utf-8 -*-
from middleware.thrift_middleware import Server
from etc.warara_settings import ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT
from etc import warara_settings

server = None


def get_server():
    '''
    현재의 Python Interpreter 에서 접속한 백엔드와 교신하게 해 준다.
    Warara 코드 전반에서 사용된다.
    '''
    global server
    if not server:
        if warara_settings.SERVER_TYPE == 'THRIFT':
            server = Server(ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT)
        elif warara_settings.SERVER_TYPE == 'DIRECT':
            from arara import arara_engine
            from arara import model
            model.init_database()
            server = arara_engine.ARAraEngine()
        else:
            raise ValueError("Invalid Value for warara_settings.SERVER_TYPE")
    return server


def set_server(new_server):
    '''
    get_server() 가 리턴하는 서버를 바꿔준다.
    '''
    global server
    server = new_server
