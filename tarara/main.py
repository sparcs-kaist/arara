#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
import sys
from ara_forms import *
from widget import *
from list_boards import *
from user_preferences import *
from welcome import *
from list_pm import *

class ara_main(ara_forms):
    menu = [
        "(N)ew article",
        "(S)elect board",
        "(P)rivate message",
        "(U)ser preferences",
        "(H)elp",
        "(A)bout ARA",
        "(W)elcome screen",
        "(Q)uit",
    ]
    def get_today_best(self):
        return [
            [u"투베갑시다", "peremen"],
	    [u"나도 투베가자","pipoket"],
	    [u"꺼져라 내가 투베간다","ssaljalu"],
	    [u"같이가요","jacob"],
	    [u"메롱 약오르지","combacsa"],
	    [u"랄라","kkhsoft"],
	]

    def get_weekly_best(self):
        return [
            [u"투베갑시다", "peremen"],
	    [u"나도 투베가자","pipoket"],
	    [u"꺼져라 내가 투베간다","ssaljalu"],
	    [u"같이가요","jacob"],
	    [u"메롱 약오르지","combacsa"],
	    [u"랄라","kkhsoft"],
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
                elif pos == 3:
                    ara_list_pm(self.session_key).main()
                elif pos==4:
                    ara_user_preferences(self.session_key).main()
                elif pos==5:
                    # TODO: 도움말로 가기
                    pass
                elif pos==6:
                    # TODO: 아라 정보 보이기
                    pass
                elif pos==7:
                    ara_welcome(self.session_key).main()
                elif pos==8:
                    sys.exit(0)
        else:
            self.frame.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Main Menu", align='center'))
        menuitems = [urwid.Text('\n')]
        menuitems +=[Item(" * "+w+"\n", None, 'selected') for w in self.menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

	self.tbtext = urwid.Filler(urwid.Text(u"Today Best", align='center'))
	tbitems = ["%(name)s (%(date)s)" % {"name":text[0], "date":text[1]} for text in self.get_today_best()]
        tbitems = [Item(w, None, 'selected') for w in tbitems]
        self.tblist = urwid.ListBox(urwid.SimpleListWalker(tbitems))
	self.todaybest = urwid.Pile([('fixed',1,self.tbtext), self.tblist])

	self.wbtext = urwid.Filler(urwid.Text(u"Weekly Best", align='center'))
	wbitems = ["%(name)s (%(date)s)" % {"name":text[0], "date":text[1]} for text in self.get_today_best()]
        wbitems = [Item(w, None, 'selected') for w in wbitems]
        self.wblist = urwid.ListBox(urwid.SimpleListWalker(wbitems))
	self.weeklybest = urwid.Pile([('fixed',1,self.wbtext), self.wblist])

	self.bests = urwid.Pile([self.todaybest, self.weeklybest])
	self.copyrightnotice = urwid.Filler(urwid.Text(
u"""  * Press [Tab] to jump between menu, today best, weekly best
 ARAra Release 1.0                                Copyright (C) 2008, SPARCS"""))

        self.maincolumn = urwid.Columns([('weight',40,self.menulist),('weight',60,self.bests)])

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
    ara_main().main()

# vim: set et ts=8 sw=4 sts=4:
