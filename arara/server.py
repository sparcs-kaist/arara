from middleware.thrift_middleware import Server
from etc.arara_settings import ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT

server = None

def get_server():
    global server
    if not server:
        server = Server(ARARA_SERVER_HOST, ARARA_SERVER_BASE_PORT)
    return server
