#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *

keymap = {
    'j': 'down',
    'k': 'up',
}

class ara_sig_intro(ara_forms):
    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Change Introduction & Signature", align='center'))

        sigtext = urwid.Filler(urwid.Text('Signature'))
        sigedit = urwid.Filler(urwid.Edit(wrap='clip'))
        introtext = urwid.Filler(urwid.Text('Introduction'))
        introedit = urwid.Filler(urwid.Edit(wrap='clip'))

	self.btnokay = urwid.Button("OK")
	self.btncancel = urwid.Button("Cancel")

        self.bottomcolumn = urwid.Filler(urwid.Columns([self.btnokay,self.btncancel]))

        content = [('fixed',1, self.header),('fixed',1,sigtext),sigedit,('fixed',1,introtext),introedit,('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_sig_intro().main()

# vim: set et ts=8 sw=4 sts=4:
