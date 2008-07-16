#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *

class ara_blacklist(ara_forms):
    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: My Blacklist",align='center'))

        okbutton = urwid.Filler(urwid.Button("OK"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(okbutton, cancelbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',1,self.dash),self.blanktext, ('fixed',1,self.dash),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_blacklist().main()

# vim: set et ts=8 sw=4 sts=4:
