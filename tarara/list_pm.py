#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *

class ara_list_pm(ara_forms):
    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Private message",align='center'))
        self.infotext = urwid.Filler(urwid.Text(" (N)ext/(P)revious Page (w)rite (B)lock (h)elp (q)uit"))

        content = [('fixed',1, self.header),('fixed',1,self.infotext),self.blanktext,]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_list_pm(session_key = "e00bc932cc2d375075f443133ae0fa44").main()

# vim: set et ts=8 sw=4 sts=4:
