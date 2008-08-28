#!/usr/bin/python
# coding: utf-8

import urwid
import urwid.raw_display
from login import *
from join import *
from welcome import *
from main import *
from list_boards import *
from user_preferences import *
from welcome import *
from list_pm import *
from user_information import *
from list_article import *
from read_article import *
from write_pm import *
from post_article import *
from change_password import *
from change_basic_info import *
from blacklist import *
from sig_intro import *
from query_user import *
from list_connected_users import *

Screen = urwid.raw_display.Screen

class ara_display:
    palette = ([
        ('header', 'black', 'dark cyan', 'bold'),
        ('selected', 'black', 'light gray', 'standout'),
        ('reversed', 'black', 'light gray', 'bold'),
        ('article_selected', 'white', 'dark red', 'bold'),
        ('menu', 'default', 'default', 'standout'),
        ('bg', 'default', 'default'),
        ('bgf', 'light gray', 'dark blue', 'standout'),
        ])
    def __init__(self):
        self.ara_login = ara_login(self)
        pass

    def change_page(self, pagename, args):
        if pagename == "login":
            self.view = self.ara_login
        if pagename == "join":
            self.view = ara_join(self, {})
        elif pagename == "welcome":
            self.view = ara_welcome(self, session_key = args['session_key'])
        elif pagename == "main":
            self.view = ara_main(self, session_key = args['session_key'])
        elif pagename == "list_boards":
            self.view = ara_list_boards(self, session_key = args['session_key'])
        elif pagename == "list_pm":
            self.view = ara_list_pm(self, session_key = args['session_key'])
        elif pagename == "write_pm":
            self.view = ara_write_pm(self, session_key = args['session_key'], mode=args['mode'], reply_to = args['reply_to'])
        elif pagename == "user_preferences":
            self.view = ara_user_preferences(self, session_key = args['session_key'])
        elif pagename == "user_information":
            self.view = ara_user_information(self, session_key = args['session_key'])
        elif pagename == "list_article":
            self.view = ara_list_article(self, args['session_key'], args['board_name'])
        elif pagename == "read_article":
            self.view = ara_read_article(self, args['session_key'], args['board_name'], args['article_id'])
        elif pagename == "post_article":
            self.view = ara_post_article(self, args['session_key'], args['board_name'], args['mode'], args['article_id'])
        elif pagename == "user_preferences":
            self.view = ara_user_preferences(self, args['session_key'])
        elif pagename == "user_information":
            self.view = ara_user_information(self, args['session_key'])
        elif pagename == "change_password":
            self.view = ara_change_password(self, args['session_key'])
        elif pagename == "blacklist":
            self.view = ara_blacklist(self, args['session_key'])
        elif pagename == "sig_intro":
            self.view = ara_sig_intro(self, args['session_key'])
        elif pagename == "query_user":
            self.view = ara_query_user(self, args['session_key'], args['default_user'])
        elif pagename == "change_basic_info":
            self.view = ara_change_basic_info(self, args['session_key'])
        elif pagename == "list_connected_users":
            self.view = ara_list_connected_users(self, args['session_key'])

    def main(self):
        self.ui = Screen()
        self.ui.register_palette(self.palette)
        self.change_page("login",{})
        self.ui.run_wrapper(self.run)

    def run(self):
        self.size = self.ui.get_cols_rows()
        while True:
            #self.view = self.ara_login
            if self.view.overlay:
                canvas = self.view.overlay.render(self.size, focus = 1)
            else:
                canvas = self.view.render(self.size, focus = 1)
            self.ui.draw_screen(self.size, canvas)
            keys = None
            while not keys:
                keys = self.ui.get_input()
                for k in keys:
                    if k =='window resize':
                        self.size = self.ui.get_cols_rows()
                    if self.view.overlay:
                        k = self.view.overlay.keypress(self.size, k)
                        if self.view.overlay.quit:
                            return
                    else:
                        k = self.view.keypress(self.size, k)

if __name__ == "__main__":
    ara_display().main()
# vim: set et ts=8 sw=4 sts=4:


