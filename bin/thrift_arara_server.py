#!/usr/bin/python
import os
import sys
import optparse
import traceback
import xmlrpclib
import time
import logging
import logging.handlers

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gen-py"))
sys.path.append(THRIFT_PATH)
sys.path.append(PROJECT_PATH)

import arara_thrift.LoginManager
import arara_thrift.ArticleManager
import arara_thrift.BlacklistManager
import arara_thrift.BoardManager
import arara_thrift.MemberManager
import arara_thrift.LoginManager
import arara_thrift.MessagingManager
import arara_thrift.NoticeManager
import arara_thrift.ReadStatusManager
import arara_thrift.SearchManager
import arara_thrift.FileManager
from arara_thrift.ttypes import *
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer

import arara
import arara.model

from thirdparty import wsgiserver

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

handler_for_info = logging.handlers.RotatingFileHandler('arara_server.log', 'a', 2**20*50, 10)
handler_for_debug = logging.handlers.RotatingFileHandler('arara_server_debug.log', 'a', 2**20*50, 10)
formatter = logging.Formatter('%(asctime)s [%(process)d:%(thread)X] <%(name)s> ** %(levelname)s ** %(message)s')
handler_for_debug.setFormatter(formatter)
handler_for_info.setFormatter(formatter)
handler_for_debug.setLevel(logging.DEBUG)
handler_for_info.setLevel(logging.INFO)

logging.getLogger('').setLevel(logging.NOTSET)
logging.getLogger('').addHandler(handler_for_debug)
logging.getLogger('').addHandler(handler_for_info)


arara.model.init_database()
namespace = arara.get_namespace()
    
from arara.article_manager import ArticleManager
from arara.blacklist_manager import BlacklistManager
from arara.board_manager import BoardManager
from arara.member_manager import MemberManager
from arara.login_manager import LoginManager
from arara.messaging_manager import MessagingManager
from arara.notice_manager import NoticeManager
from arara.read_status_manager import ReadStatusManager
from arara.search_manager import SearchManager
from arara.file_manager import FileManager

MAPPING = [(LoginManager, arara_thrift.LoginManager),
           (MemberManager, arara_thrift.MemberManager),
           (BlacklistManager, arara_thrift.BlacklistManager),
           (BoardManager, arara_thrift.BoardManager),
           (ReadStatusManager, arara_thrift.ReadStatusManager),
           (ArticleManager, arara_thrift.ArticleManager),
           (MessagingManager, arara_thrift.MessagingManager),
           (NoticeManager, arara_thrift.NoticeManager),
           (ReadStatusManager, arara_thrift.ReadStatusManager),
           (SearchManager, arara_thrift.SearchManager),
           (FileManager, arara_thrift.FileManager)
           ]

DEPENDENCY = {LoginManager: [MemberManager],
              MemberManager: [LoginManager],
              BlacklistManager: [MemberManager, LoginManager],
              BoardManager: [LoginManager],
              ReadStatusManager: [LoginManager, MemberManager],
              ArticleManager: [LoginManager, BlacklistManager,
                               ReadStatusManager, BoardManager,
                               FileManager],
              MessagingManager: [LoginManager, MemberManager,
                                 BlacklistManager],
              NoticeManager: [LoginManager, MemberManager],
              ReadStatusManager: [LoginManager, MemberManager],
              SearchManager: [BoardManager, LoginManager],
              FileManager: [LoginManager]
              }

PORT = {LoginManager: 1,
        MemberManager: 2,
        BlacklistManager: 3,
        BoardManager: 4,
        ReadStatusManager: 5,
        ArticleManager: 6,
        MessagingManager: 7,
        NoticeManager: 8,
        ReadStatusManager: 9,
        SearchManager: 10,
        FileManager: 11,
        }

CLASSES = {'LoginManager': LoginManager,
           'MemberManager': MemberManager,
           'BlacklistManager': BlacklistManager,
           'BoardManager': BoardManager,
           'ReadStatusManager': ReadStatusManager,
           'ArticleManager': ArticleManager,
           'MessagingManager': MessagingManager,
           'NoticeManager': NoticeManager,
           'ReadStatusManager': ReadStatusManager,
           'SearchManager': SearchManager,
           'FileManager': FileManager,
        }

def open_thrift_server(processor, handler, port):
    handler_instance = handler()
    processor_ = processor.Processor(handler_instance)
    transport = TSocket.TServerSocket(port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadedServer(processor_, transport, tfactory, pfactory)
    return server, handler_instance

def connect_thrift_server(host, port, thrift_class):
    transport = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = thrift_class.Client(protocol)
    transport.open()
    return client

def setter_name(class_):
    """AbcdEfg -> _set_abcd_efg"""
    class_name = class_.__name__
    char_list = list(class_name)
    if char_list[0].isupper():
        char_list[0] = char_list[0].lower()
    for i, char in enumerate(char_list):
        if char.isupper():
            char_list[i] = char.lower()
            char_list.insert(i, '_')
    concat = ''.join(char_list)
    return '_set_' + concat

def open_server(server_name, base_port):
    assert server_name in CLASSES
    base_class = CLASSES[server_name]
    thrift_class = dict(MAPPING)[base_class]
    port = base_port + PORT[base_class]
    import thread
    server, instance = open_thrift_server(thrift_class, base_class, port)
    thread.start_new_thread(resolve_dependencies, (base_class, instance, base_port))
    return server

def resolve_dependencies(base_class, instance, base_port):
    dependencies = DEPENDENCY[base_class]
    for dependency_class in dependencies:
        dependency_port = base_port + PORT[dependency_class]
        dependency_thrift_class = dict(MAPPING)[dependency_class]
        print 'Connecting to %s in localhost:%d' % (
                dependency_class.__name__, dependency_port)
        while True:
            try:
                client = connect_thrift_server('localhost',
                        dependency_port, dependency_thrift_class)
                setter = setter_name(dependency_class)
                setter_method = getattr(instance, setter)
                setter_method(client)
                break
            except TTransportException:
                print '%s cannot be connected. Retrying...' % dependency_class.__name__
                time.sleep(1)
                continue
    

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port=", dest="port", default=8000, type="int",
                      help="The port to bind")
    options, args = parser.parse_args()
    print "Opening ARAra Thrift middleware on port starting from", options.port, "..."
    
    servers = []

    def exception_handler(type_, value, traceback_):
        import traceback
        error_msg = ''.join(traceback.format_exception(type_, value, traceback_))
        print >> sys.stderr, error_msg
        print >> sys.stdout, error_msg

    sys.excepthook = exception_handler

    print args[0]
    server = open_server(args[0], options.port)

    print 'Starting the server...'
    server.serve()
    print 'done.'
    

# vim: set et ts=8 sw=4 sts=4
