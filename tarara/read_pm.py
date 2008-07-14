#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from common import *

keymap = {
    'j': 'down',
    'k': 'up',
}

class ara_read_pm(ara_forms):
    def get_current_board(self):
	return "garbages"

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Read private message",align='center'))
        functext = urwid.Filler(urwid.Text('(n)ext/(p)revious (b)lock (d)elete (r)eply (h)elp (q)uit'))
	titletext = urwid.Filler(urwid.Text('Title: %s' % "윅베간다"))
	infotext = urwid.Filler(urwid.Text('Sender: %(id)s (%(nickname)s)     %(date)s' % {'id':'peremen', 'nickname':'peremen','date':'today'}))

        content = [('fixed',1, self.header),('fixed',1,functext),('fixed',1,titletext),('fixed',1,infotext),('fixed',1,self.dash),self.blanktext]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__ == "__main__":
    ara_pm_read().main()

# vim: set et ts=8 sw=4 sts=4:
