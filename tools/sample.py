import sys
import os

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './gen-py/'))
sys.path.append(PROJECT_PATH)
sys.path.append(THRIFT_PATH)

from arara import server

def main():
    session_key_sysop = server.get_server().login_manager.login("SYSOP", "together2happy!", "127.0.0.1")
    hmm = server.get_server().article_manager.get_today_best_list(5)
    print repr(hmm)

if __name__ == "__main__":
    main()
