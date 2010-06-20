#-*- coding: utf-8 -*-
from arara_engine_connector import *
# Now 'get_server' is available. 

LOGIN_ID = 'SYSOP'
LOGIN_PW = 'SYSOP'

def board_handle(session_key, board_name):
    print "Handling for board name [", board_name, "]"
    root_article_list = get_server().article_manager.article_list(session_key, board_name, 1, 1048576)
    root_article_list_hit = root_article_list.hit
    print "There are", len(root_article_list_hit), "articles."
    for i in xrange(len(root_article_list_hit)):
        get_server().article_manager.fix_reply_count(session_key, board_name, root_article_list_hit[i].id)
        get_server().article_manager.destroy_article(session_key, board_name, root_article_list_hit[i].id)
        if i % 10 == 0:
            print i, "/", len(root_article_list_hit)
    print "Done for board name [", board_name, "]"

def login():
    return get_server().login_manager.login(LOGIN_ID, LOGIN_PW, '127.0.0.1')

def logout(session_key):
    get_server().login_manager.logout(session_key)

def main():
    session_key = login()
    board_handle(session_key, 'test')
    logout(session_key)

if __name__ == "__main__":
    main()
