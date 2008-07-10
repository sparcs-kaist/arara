#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from common import *

keymap = {
    'j': 'down',
    'k': 'up',
}

class ara_welcome(ara_forms):
    def get_banner(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'banner.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def get_ip(self):
        return "127.0.0.1"

    def get_location(self):
        return "Web"

    def get_date(self):
        return "Today"

    def __initwidgets__(self):
        self.banner = urwid.Filler(urwid.Text(self.get_banner()))

        logintext = "Last login: %(IP)s/%(location)s at %(date)s"
        logindata = {"IP": self.get_ip(), "location": self.get_location(), "date":self.get_date()}
        self.logininfo = urwid.Filler(urwid.Text(logintext % logindata))

        self.entertext = urwid.Filler(urwid.Text("Press [Enter] key to continue"))

        content = [self.banner,('fixed',1, self.logininfo),('fixed',1,self.blank), ("fixed", 1, self.entertext)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

ara_welcome().main()

# vim: set et ts=8 sw=4 sts=4
