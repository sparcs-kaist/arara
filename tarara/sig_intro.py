#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *

class ara_sig_intro(ara_forms):
    def on_button_clicked(self, button):
        self.myinfo['signature'] = self.sigedit.body.get_edit_text()
        self.myinfo['self_introduce'] = self.introedit.body.get_edit_text()
        print self.server.member_manager.modify(self.session_key, self.myinfo)

    def set_sig_intro(self):
        self.sigedit.body.set_edit_text(self.myinfo['signature'])
        self.introedit.body.set_edit_text(self.myinfo['self_introduction'])

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Change Introduction & Signature", align='center'))
        self.myinfo = self.server.member_manager.get_info(self.session_key)
        self.myinfo = self.myinfo[1]

        sigtext = urwid.Filler(urwid.Text('Signature'))
        self.sigedit = urwid.Filler(urwid.Edit(wrap='clip'))
        introtext = urwid.Filler(urwid.Text('Introduction'))
        self.introedit = urwid.Filler(urwid.Edit(wrap='clip'))

	self.btnokay = urwid.Button("OK", self.on_button_clicked)
	self.btncancel = urwid.Button("Cancel", self.on_button_clicked)

        self.bottomcolumn = urwid.Filler(urwid.Columns([self.btnokay,self.btncancel]))

        content = [('fixed',1, self.header),
                ('fixed',1,sigtext),
                ('fixed',1,self.dash),
                self.sigedit,
                ('fixed',1,self.dash),
                ('fixed',1,introtext),
                ('fixed',1,self.dash),
                self.introedit,
                ('fixed',1,self.dash),
                ('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        self.set_sig_intro()

        return self.mainpile

if __name__=="__main__":
    ara_sig_intro().main()

# vim: set et ts=8 sw=4 sts=4:
