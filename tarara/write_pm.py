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

class ara_write_pm(ara_forms):
    def get_current_board(self):
	return "garbages"

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Write private message", align='center'))

        titleedit = urwid.Filler(urwid.Edit(caption="Title: ", wrap='clip'))
        idedit = urwid.Edit(caption="To (Enter ID): ", wrap='clip')
	self.btnsearch = urwid.Button("Search by nickname")
        self.idcolumn = urwid.Filler(urwid.Columns([('weight',60,idedit),('weight',40,self.btnsearch)]))
	self.info = urwid.Filler(urwid.Text(u"* You can use semicolon(;) to send two or more person."))

        bodytext = urwid.Filler(urwid.Text('Body'))
        self.bodyedit = urwid.Filler(urwid.Edit(multiline = True, wrap='clip'))

	self.btnhelp = urwid.Button("Help")
	self.btnpreview = urwid.Button("Preview")
	self.btnokay = urwid.Button("Send")
	self.btncancel = urwid.Button("Cancel")

        self.bottomcolumn = urwid.Filler(urwid.Columns([('weight',40,urwid.Text(' ')),('weight',15,self.btnhelp),('weight',15,self.btnpreview),('weight',15,self.btnokay),('weight',15,self.btncancel)]))

        content = [('fixed',1, self.header),('fixed',1,titleedit),('fixed',1,self.idcolumn),('fixed',1,self.info),('fixed',1,bodytext),('fixed',1,self.dash),self.bodyedit,('fixed',1,self.dash),('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_write_pm().main()

# vim: set et ts=8 sw=4 sts=4:
