#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from widget import *
from ara_forms import *

class ara_user_information(ara_forms):
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
    def __keypress__(self, size, key):
        self.frame.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: User Information", align='center'))
        menuitems = [Item(" * "+w+"\n", None, 'selected') for w in self.menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

        menudescs = [Item(w, None, 'selected') for w in self.menudesc]
        self.menudesclist = urwid.ListBox(urwid.SimpleListWalker(menudescs))

        self.maincolumn = urwid.Columns([('weight',40,self.menulist),('weight',60,self.menudesclist)])

        infotext = urwid.Filler(urwid.Text("  * Use [Tab] or arrow key to move each items"))

        self.okbutton = urwid.Filler(urwid.Button("OK"))
        self.cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        self.buttoncolumn = self._make_column(self.okbutton, self.cancelbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',1,self.dash),self.maincolumn,('fixed',1,self.dash),('fixed',1,infotext),('fixed',2,self.buttoncolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_user_information().main()

# vim: set et ts=8 sw=4 sts=4:
