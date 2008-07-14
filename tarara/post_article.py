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

class ara_postarticle(ara_forms):
    def get_current_board(self):
	return "garbages"

    def __initwidgets__(self, modify = False):
        if modify:
            self.header = urwid.Filler(urwid.Text(u"ARA: Modify Article  Current board: %s" % self.get_current_board(), align='center'))
	else:
            self.header = urwid.Filler(urwid.Text(u"ARA: Post Article  Current board: %s" % self.get_current_board(), align='center'))

        titleedit = urwid.Filler(urwid.Edit(caption="Title: ", wrap='clip'))
        bodytext = urwid.Filler(urwid.Text('Body'))
        self.bodyedit = urwid.Filler(urwid.Edit(multiline = True, wrap='clip'))

	self.chkinclude = urwid.CheckBox("Include in search")
	self.btnhelp = urwid.Button("Help")
	self.btnpreview = urwid.Button("Preview")
	self.btnokay = urwid.Button("OK")
	self.btncancel = urwid.Button("Cancel")

        self.bottomcolumn = urwid.Filler(urwid.Columns([('weight',40,self.chkinclude),('weight',15,self.btnhelp),('weight',15,self.btnpreview),('weight',15,self.btnokay),('weight',15,self.btncancel)]))

        content = [('fixed',1, self.header),('fixed',1,titleedit),('fixed',1,bodytext),('fixed',1,self.dash),self.bodyedit,('fixed',1,self.dash),('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_postarticle().main()

# vim: set et ts=8 sw=4 sts=4:
