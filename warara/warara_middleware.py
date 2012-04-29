#-*- coding: utf-8 -*-
from middleware.thrift_middleware import Server
from etc.warara_settings import ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT
from etc import warara_settings

import logging

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
            # Set logger
            # XXX(hodduc): Thrift server와 arara_settings를 참조하지 않는 방향으로 고치면 더 좋을 듯
            # bin/thrift_arara_server.py와 middleware/thrift_server.py에서 해당 부분을 분리해낼 필요가 있음
            from middleware.thrift_server import set_default_log_handlers
            from etc import arara_settings
            set_default_log_handlers(arara_settings.ARARA_LOG_PATH,
                    arara_settings.ARARA_DEBUG_HANDLER_ON,
                    arara_settings.ARARA_DEBUG_LOG_PATH)
            logger = logging.getLogger('main')

            # Get Engine
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
