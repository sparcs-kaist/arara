#-*- coding: utf-8 -*-
from arara_engine_connector import *
# Now 'get_server' is available. 

LOGIN_ID = 'SYSOP'
LOGIN_PW = 'SYSOP'

def board_handle(session_key, board_name):
    root_article_list = get_server().article_manager.article_list(session_key, board_name, 1, 1048576)
    root_article_list_hit = root_article_list.hit
    for i in xrange(len(root_article_list_hit)):
        print get_server().article_manager.fix_reply_count(session_key, board_name, root_article_list_hit[i].id)
        if root_article_list_hit[i].reply_count < 0:
            print "reply_count < 0"
            break

def login():
    return get_server().login_manager.login(LOGIN_ID, LOGIN_PW, '127.0.0.1')

def logout(session_key):
    get_server().login_manager.logout(session_key)

def main():
    session_key = login()
    board_handle(session_key, 'garbages')
    logout(session_key)

if __name__ == "__main__":
    main()
