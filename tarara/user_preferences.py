#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from widget import *
from ara_forms import *

class ara_user_preferences(ara_forms):
    menu = [
        "(L)ist all users",
        "List (c)onnected users",
        "(M)onitor connected users",
        "(Q)uery user",
    ]
    menudesc = [
        "Show all registered users\n",
        "Show information about\ncurrent users",
        "Monitor current users\n",
        "Query about user's last used\nIP, introduction, etc.",
    ]

    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def __initwidgets__(self):
	header = urwid.Filler(urwid.Text("ARA: User Preferences", align='center'))

        menuitems = [Item(" * "+w+"\n", None, 'selected') for w in self.menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

        menudescs = [Item(w, None, 'selected') for w in self.menudesc]
        self.menudesc = urwid.ListBox(urwid.SimpleListWalker(menudescs))

        menucolumn = self._make_column(self.menulist, self.menudesc)

        infotext = urwid.Filler(urwid.Text("  * Use [Tab] or arrow key to move each items"))

        okbutton = urwid.Filler(urwid.Button("OK"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(okbutton, cancelbutton, 50, 50)

        content = [('fixed',1,header),menucolumn,('fixed',1,self.dash),('fixed',1,infotext),('fixed',1,self.blank),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_user_preferences().main()

# vim: set et ts=8 sw=4 sts=4:
