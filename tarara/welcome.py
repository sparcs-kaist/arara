#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_welcome(ara_form):
    def get_banner(self):
	retvalue, banner = self.server.notice_manager.get_welcome()
        if retvalue:
            return banner[1]
        else:
            return u"오늘의 환영 인사는 없습니다."

    def keypress(self, size, key):
        if "enter" in key:
            self.parent.change_page("main",{'session_key':self.session_key})

    def __initwidgets__(self):
        self.banner = urwid.Filler(urwid.Text(self.get_banner()))
        retvalue, myinfo = self.server.member_manager.get_info(self.session_key)
        assert retvalue, myinfo

        logintext = "Last login: %(IP)s at %(date)s"
        logindata = {"IP": myinfo['last_login_ip'], "date":myinfo['last_logout_time'].strftime("%Y/%m/%d %H:%M:%S")}
        self.logininfo = urwid.Filler(urwid.Text(logintext % logindata))

        self.entertext = urwid.Filler(urwid.Text("Press [Enter] key to continue"))

        content = [self.banner,('fixed',1, self.logininfo),('fixed',1,widget.blank), ("fixed", 1, self.entertext)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_welcome().main()

# vim: set et ts=8 sw=4 sts=4:
