MANAGER_LIST = (
        'login_manager',
        'member_manager',
        'blacklist_manager',
        'board_manager',
        'read_status_manager',
        'article_manager',
        'messaging_manager',
        'notice_manager',
        'read_status_manager',
        'search_manager',
        'file_manager',
               )

HANDLER_PORT = dict(zip(MANAGER_LIST, range(1, len(MANAGER_LIST) + 1)))

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
        'read_status_manager': ['login_manager', 'member_manager'],
        'search_manager': ['board_manager', 'login_manager'],
        'file_manager': ['login_manager']
              }
