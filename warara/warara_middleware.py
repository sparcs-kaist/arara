#-*- coding: utf-8 -*-
from middleware.thrift_middleware import Server
from etc.warara_settings import ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT

server = None


def get_server():
    '''
    현재의 Python Interpreter 에서 접속한 백엔드와 교신하게 해 준다.
    Warara 코드 전반에서 사용된다.
    '''
    global server
    if not server:
        server = Server(ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT)
    return server


def set_server(new_server):
    '''
    get_server() 가 리턴하는 서버를 바꿔준다.
    '''
    global server
    server = new_server
