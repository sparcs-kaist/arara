#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from widget import *
from ara_forms import *
from query_user import *

class ara_user_information(ara_forms):
    menu = [
        "(L)ist all users",
        "List (c)onnected users",
        "(M)onitor connected users",
        "(Q)uery user",
        "(E)xit menu",
    ]
    menudesc = [
        "Show all registered users\n",
        "Show information about\ncurrent users",
        "Monitor current users\n",
        "Query about user's last used\nIP, introduction, etc.",
        "Return to main menu",
    ]

    def __keypress__(self, size, key):
        key = key.strip().lower()
        if key == "enter":
            pos = self.menulist.get_focus()[1]
            if pos == 0:
                # TODO: 모든 사용자 보여주기
                pass
            elif pos == 1:
                # TODO: 연결된 사용자 보여주기
                pass
            elif pos == 2:
                # TODO: 연결된 사용자 관찰하기
                pass
            elif pos==3:
                ara_query_user(self.session_key).main()
            elif pos==4:
                # TODO: 이전 메뉴로 돌아가기
                pass
        else:
            self.frame.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: User Information", align='center'))
        menuitems = [Item(" * "+w+"\n", None, 'selected') for w in self.menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

        menudescs = [Item(w, None, 'selected') for w in self.menudesc]
        self.menudesclist = urwid.ListBox(urwid.SimpleListWalker(menudescs))

        self.maincolumn = urwid.Columns([('weight',40,self.menulist),('weight',60,self.menudesclist)])

        infotext = urwid.Filler(urwid.Text("  * Use [Tab] or arrow key to move each items"))

        content = [('fixed',1, self.header),('fixed',1,self.dash),self.maincolumn,('fixed',1,self.dash),('fixed',1,infotext),]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_user_information().main()

# vim: set et ts=8 sw=4 sts=4:
