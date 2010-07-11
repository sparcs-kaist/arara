#-*- coding: utf-8 -*-
from middleware.thrift_middleware import Server
from etc.arara_settings import ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT

server = None

def get_server():
    '''
    현재의 Python Interpreter 에서 접속한 백엔드와 교신하게 해 준다.
    '''
    global server
    if not server:
        server = Server(ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT)
    return server
