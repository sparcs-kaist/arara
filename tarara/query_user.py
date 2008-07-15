#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *

class ara_query_user(ara_forms):
    def __initwidgets__(self):
        self.keymap = {
            'j': 'down',
            'k': 'up',
        }
	self.header = urwid.Filler(urwid.Text(u"ARA: Query User",align='center'))
        self.idedit = urwid.Filler(urwid.Edit(caption=" * Enter ID: ", wrap='clip'))
        self.btnsearch = urwid.Filler(urwid.Button("Search by nickname"))
        self.btncancel = urwid.Filler(urwid.Button("Cancel"))

        self.buttoncolumn = urwid.Columns([('weight', 70, self.idedit), ('weight', 20, self.btnsearch),('weight',10,self.btncancel)])

	idtext = urwid.Filler(urwid.Text(' * ID: %s' % "serialx"))
	nicktext = urwid.Filler(urwid.Text(' * Nickname: %s' % "polarbear"))
	introtext = urwid.Filler(urwid.Text(' * Introduction:\n %s' % "I am polarbear"))
	sigtext = urwid.Filler(urwid.Text(' * Signature:\n %s' % "I am polarbear"))
	lasttext = urwid.Filler(urwid.Text(' * Last usage: %s' % "Today @ telnet"))

	actiontext = urwid.Filler(urwid.Text(' * Press [Enter] to query another user, [q] to quit'))

        content = [('fixed',1, self.header),
            ('fixed',1,self.buttoncolumn),
            ('fixed',1,idtext),
            ('fixed',1,nicktext),
            ('fixed',6,introtext),
            ('fixed',6,sigtext),
            ('fixed',1,lasttext),
            actiontext,
            ]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_query_user().main()

# vim: set et ts=8 sw=4 sts=4:
