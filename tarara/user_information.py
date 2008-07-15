#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from widget import *
from common import *

class ara_user_information(ara_forms):
    menu = [
        "(L)ist all users",
        "List (c)onnected users",
        "(M)onitor connected users",
        "(Q)uery user",
    ]
    def __keypress__(self, size, key):
        key = key.strip().lower()
        if key == "tab":
            if self.maincolumn.get_focus() == self.menulist:
                self.maincolumn.set_focus(self.bests)
            elif self.maincolumn.get_focus() == self.bests:
                self.maincolumn.set_focus(self.menulist)
        elif key == "enter":
            if self.maincolumn.get_focus() == self.menulist:
                pos = self.menulist.get_focus()[1]
                if pos == 1:
                    # TODO: 새 글 읽기로 가기
                    pass
                elif pos == 2:
                    ara_list_boards(self.session_key).main()
        else:
            self.frame.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: User Information", align='center'))
        menuitems = [urwid.Text('\n')]
        menuitems +=[Item(" * "+w+"\n", None, 'selected') for w in self.menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

        self.maincolumn = urwid.Columns([('weight',40,self.menulist),('weight',60,self.bests)])

        infotext = urwid.Filler(urwid.Text("  * Use [Tab] or arrow key to move each items"))

        okbutton = urwid.Filler(urwid.Button("OK"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(okbutton, cancelbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',1,self.dash),self.maincolumn,('fixed',1,self.dash),('fixed',2,self.copyrightnotice)]
        self.mainpile = urwid.Pile(content)

        self.keymap = {
            "left":"",
            "right":"",
            "j":"down",
            "k":"up",
            }

        return self.mainpile

if __name__=="__main__":
    ara_user_information().main()

# vim: set et ts=8 sw=4 sts=4:
