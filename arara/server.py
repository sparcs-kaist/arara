from middleware.thrift_middleware import Server

server = None

def get_server():
    global server
    if not server:
        server = Server()
    return server
