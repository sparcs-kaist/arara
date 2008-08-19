#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_user_preferences(ara_form):
    menu = [
        "Change Basic information",
        "Change Password",
        "View/edit Blacklist",
        "Change Introduction/Signature",
        "Zap Board",
        "Set Terminal Encoding",
        "Exit menu",
    ]
    menudesc = [
        "Change basic information like nickname and email",
        "Change password\n",
        "View and edit your blacklist\n",
        "Change intruduction and signature used in the articles",
        "Zap board\n",
        "Set your terminal encoding\n",
        "Return to main menu\n",
    ]

    def keypress(self, size, key):
        if key == "enter":
            pos = self.menulist.get_focus()[1]
            if pos == 0:
                self.parent.change_page("change_basic_info", {'session_key':self.session_key})
            elif pos == 1:
                self.parent.change_page("change_password", {'session_key':self.session_key})
            elif pos == 2:
                self.parent.change_page("blacklist", {'session_key':self.session_key})
            elif pos == 3:
                self.parent.change_page("sig_intro", {'session_key':self.session_key})
            elif pos == 4:
                # TODO: 잽
                pass
            elif pos == 5:
                # TODO: 인코딩 설정
                pass
            elif pos == 6:
                self.parent.change_page("main",{'session_key':self.session_key})
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: User Preferences", align='center'))
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
