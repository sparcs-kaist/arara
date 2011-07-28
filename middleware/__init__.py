#-*- coding: utf-8 -*-
'''
ARAra Middleware Definition
'''

# Backend 에 존재하는 Manager 들의 목록.
MANAGER_LIST = (
        'login_manager',
        'member_manager',
        'blacklist_manager',
        'board_manager',
        'read_status_manager',
        'article_manager',
        'messaging_manager',
        'notice_manager',
        'search_manager',
        'file_manager',
        'bot_manager',
               )

# 각각의 Manager 들의 의존관계.
# list 에 명시된 Manager 가 준비되어야 정상 작동함을 뜻한다.
# bin/thrift_arara_server.py 에서 각 Manager 에 대한 Middleware 가 준비되었는지
# 검사하기 위해 도입되었는데, fa96e4727daa 에 의해 현재는 쓰이지 않고 있다.
DEPENDENCY = {
        'login_manager': ['member_manager'],
        'member_manager': ['login_manager'],
        'blacklist_manager': ['member_manager', 'login_manager'],
        'board_manager': ['login_manager'],
        'read_status_manager': ['login_manager', 'member_manager'],
        'article_manager': ['login_manager', 'blacklist_manager',
                            'read_status_manager', 'board_manager',
                            'file_manager'],
        'messaging_manager': ['login_manager', 'member_manager',
                              'blacklist_manager'],
        'notice_manager': ['login_manager', 'member_manager'],
        'search_manager': ['board_manager', 'login_manager'],
        'file_manager': ['login_manager'],
        'bot_manager': ['login_manager', 'member_manager',
                        'article_manager', 'board_manager'],
              }
