#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *

class ara_list_allusers(ara_forms):
    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: List all users",align='center'))
        self.querytext = urwid.Filler(urwid.Edit(caption=" * Search: ", wrap='clip'))
        self.infotext = urwid.Filler(urwid.Text("(q)uit (Enter) query"))

        okbutton = urwid.Filler(urwid.Button("OK"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(okbutton, cancelbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',1,self.querytext),('fixed',1,self.infotext),('fixed',1,self.dash),self.blanktext, ]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_list_allusers().main()

# vim: set et ts=8 sw=4 sts=4:
