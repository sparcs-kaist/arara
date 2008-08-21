#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_user_information(ara_form):
    menu = [
        "List (c)onnected users",
        "(M)onitor connected users",
        "(Q)uery user",
        "(E)xit menu",
    ]
    menudesc = [
        "Show information about\ncurrent users",
        "Monitor current users\n",
        "Query about user's last used\nIP, introduction, etc.",
        "Return to main menu",
    ]

    def keypress(self, size, key):
        if key == "enter":
            pos = self.menulist.get_focus()[1]
            if pos == 0:
                self.parent.change_page("list_connected_users", {'session_key':self.session_key})
            elif pos == 1:
                # TODO: 연결된 사용자 관찰하기
                pass
            elif pos == 2:
                self.parent.change_page("query_user", {'session_key':self.session_key})
            elif pos == 3:
                self.parent.change_page("main", {'session_key':self.session_key})
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: User Information", align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        menuitems = [widget.Item(" * "+w+"\n", None, 'selected') for w in self.menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

        menudescs = [widget.Item(w, None, 'selected') for w in self.menudesc]
        self.menudesclist = urwid.ListBox(urwid.SimpleListWalker(menudescs))

        self.maincolumn = urwid.Columns([('weight',40,self.menulist),('weight',60,self.menudesclist)])

        infotext = urwid.Filler(urwid.Text("  * Use [Tab] or arrow key to move each items"))

        content = [('fixed',1, self.header),('fixed',1,widget.blanktext),
                self.maincolumn,('fixed',1,widget.dash),
                ('fixed',1,infotext),]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_user_information().main()

# vim: set et ts=8 sw=4 sts=4:
