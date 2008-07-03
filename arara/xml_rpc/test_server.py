from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import sys
PROJECT_PATH=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(PROJECT_PATH)
from arara.article_manager import ArticleManager
from arara.blacklist_manager import BlacklistManager
from arara.login_manager import LoginManager

class Namespace(object):
    article_manager = ArticleManager()
    blacklist_manager = BlacklistManager()
    login_manager = LoginManager()

server = SimpleXMLRPCServer(("",3939))
server.register_introspection_functions()

server.register_instance(Namespace(), allow_dotted_names=True)

server.serve_forever()
