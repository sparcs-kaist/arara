#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
from translation import _

class ara_welcome(ara_form):
    def get_banner(self):
	retvalue, banner = self.server.notice_manager.get_welcome()
        if retvalue:
            return banner[1]
        else:
            return _('No welcome message for today.')

    def keypress(self, size, key):
        if "enter" in key:
            self.parent.change_page("main",{'session_key':self.session_key})

    def __initwidgets__(self):
        self.banner = urwid.Filler(urwid.Text(self.get_banner()))

        if self.session_key == 'guest':
            logintext = _('You are in guest mode.')
            self.logininfo = urwid.Filler(urwid.Text(logintext))
        else:
            logintext = _('Last login: %(IP)s at %(date)s')
            retvalue, myinfo = self.server.member_manager.get_info(self.session_key)
            assert retvalue, myinfo
            if myinfo['last_logout_time'] == 'NOT AVAILABLE':
                logindata = {'IP': myinfo['last_login_ip'], 'date':'Unknown'}
            else:
                logindata = {'IP': myinfo['last_login_ip'], 'date':myinfo['last_logout_time'].strftime("%Y/%m/%d %H:%M:%S")}
            self.logininfo = urwid.Filler(urwid.Text(logintext % logindata))

        self.entertext = urwid.Filler(urwid.Text(_('Press [Enter] key to continue')))

        content = [self.banner,('fixed',1, self.logininfo),('fixed',1,widget.blank), ("fixed", 1, self.entertext)]
        self.mainpile = urwid.Pile(content)

# vim: set et ts=8 sw=4 sts=4:
