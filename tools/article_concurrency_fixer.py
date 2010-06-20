#-*- coding: utf-8 -*-
'''
Article Concurrency Fixier

ARAra 엔진에 직접 접근하여 각각의 글에 대한 정보가 잘못 저장된 것을 교정한다.

Implemented:
    1) Reply Count
    2) Destroyed
Not yet Implemented:
    3) Last Reply Date
    4) Last Reply ID
'''

from arara_engine_connector import *

LOGIN_ID = 'SYSOP'
LOGIN_PW = 'SYSOP'

MAXIMUM_LENGTH = 1048576

def board_handle(session_key, board_name):
    print "Handling for board name [", board_name, "]"

    root_article_list = get_server().article_manager.article_list(session_key, board_name, 1, MAXIMUM_LENGTH)
    root_article_list_hit = root_article_list.hit
    length = len(root_article_list_hit)

    print "There are", length, "articles."

    for idx, article in enumerate(root_article_list_hit):
        get_server().article_manager.fix_article_concurrency(session_key, board_name, article.id)
        if idx % 10 == 0:
            print idx, "/", length

    print "Done for board name [", board_name, "]"

def login():
    return get_server().login_manager.login(LOGIN_ID, LOGIN_PW, '127.0.0.1')

def logout(session_key):
    get_server().login_manager.logout(session_key)

def get_board_list():
    board_list = get_server().board_manager.get_board_list()
    return [board.board_name for board in board_list]

def main():
    session_key = login()
    board_list  = get_board_list()
    for board_name in board_list:
        board_handle(session_key, board_name)
    logout(session_key)

if __name__ == "__main__":
    main()
