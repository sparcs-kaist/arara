#!/usr/bin/python
# coding: utf-8

import urwid
import urwid.curses_display
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
from blacklist import *
from sig_intro import *
from query_user import *
from helpviewer import *

Screen = urwid.curses_display.Screen

class ara_display:
    palette = ([
        ('header', 'black', 'dark cyan', 'standout'),
        ('selected', 'default', 'light gray', 'bold'),
        ('reversed', 'white', 'black', 'bold'),
        ])
    def __init__(self):
        self.ara_login = ara_login(self)
        pass

    def change_page(self, pagename, args):
        if pagename == "login":
            self.view = self.ara_login
        if pagename == "join":
            self.ara_join = ara_join(self, {})
            self.view = self.ara_join
        elif pagename == "welcome":
            self.ara_welcome = ara_welcome(self, session_key = args['session_key'])
            self.view = self.ara_welcome
        elif pagename == "main":
            self.ara_main = ara_main(self, session_key = args['session_key'])
            self.view = self.ara_main
        elif pagename == "list_boards":
            self.ara_list_boards = ara_list_boards(self, session_key = args['session_key'])
            self.view = self.ara_list_boards
        elif pagename == "list_pm":
            self.ara_list_pm = ara_list_pm(self, session_key = args['session_key'])
            self.view = self.ara_list_pm
        elif pagename == "write_pm":
            self.ara_write_pm = ara_write_pm(self, session_key = args['session_key'], mode=args['mode'], reply_to = args['reply_to'])
            self.view = self.ara_write_pm
        elif pagename == "user_preferences":
            self.ara_user_preferences = ara_user_preferences(self, session_key = args['session_key'])
            self.view = self.ara_user_preferences
        elif pagename == "user_information":
            self.ara_user_information = ara_user_information(self, session_key = args['session_key'])
            self.view = self.ara_user_information
        elif pagename == "list_article":
            self.ara_list_article = ara_list_article(self, args['session_key'], args['board_name'])
            self.view = self.ara_list_article
        elif pagename == "read_article":
            self.ara_read_article = ara_read_article(self, args['session_key'], args['board_name'], args['article_id'])
            self.view = self.ara_read_article
        elif pagename == "post_article":
            self.ara_post_article = ara_post_article(self, args['session_key'], args['board_name'], args['mode'], args['article_id'])
            self.view = self.ara_post_article
        elif pagename == "user_preferences":
            self.ara_user_preferences = ara_user_preferences(self, args['session_key'])
            self.view = self.ara_user_preferences
        elif pagename == "user_information":
            self.ara_user_information = ara_user_information(self, args['session_key'])
            self.view = self.ara_user_information
        elif pagename == "change_password":
            self.ara_change_password = ara_change_password(self, args['session_key'])
            self.view = self.ara_change_password
        elif pagename == "blacklist":
            self.ara_blacklist = ara_blacklist(self, args['session_key'])
            self.view = self.ara_blacklist
        elif pagename == "sig_intro":
            self.ara_sig_intro = ara_sig_intro(self, args['session_key'])
            self.view = self.ara_sig_intro
        elif pagename == "query_user":
            self.ara_query_user = ara_query_user(self, args['session_key'])
            self.view = self.ara_query_user
        elif pagename == "helpviewer":
            self.ara_helpviewer = ara_helpviewer(self, args['session_key'], args['topic'], args['caller'], args['caller_args'])
            self.view = self.ara_helpviewer

    def main(self):
        self.ui = Screen()
        self.ui.register_palette(self.palette)
        self.change_page("login",{})
        self.ui.run_wrapper(self.run)

    def run(self):
        size = self.ui.get_cols_rows()
        while True:
            #self.view = self.ara_login
            canvas = self.view.render(size, focus = 1)
            self.ui.draw_screen(size, canvas)
            keys = None
            while not keys:
                keys = self.ui.get_input()
                for k in keys:
                    if k =='window resize':
                        size = self.ui.get_cols_rows()
                    k = self.view.keypress(size, k)

if __name__ == "__main__":
    ara_display().main()
# vim: set et ts=8 sw=4 sts=4:


