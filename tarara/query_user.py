#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_query_user(ara_form):
    def keypress(self, size, id):
        self.mainpile.keypress(size, id)

    def on_button_clicked(self, button):
        if button == self.btnsearch.body:
            self.query_information(self.idedit.body.get_edit_text())
        elif button == self.btncancel.body:
            self.parent.change_page("user_information", {'session_key':self.session_key})

    def query_information(self, id):
        a = self.server.member_manager.query_by_username(self.session_key, id)
        if a[1] == 'QUERY_ID_NOT_EXIST':
            return
        a = a[1]
	self.idtext.body.set_text(' * ID: %s' % a['username'])
	self.nicktext.body.set_text(' * Nickname: %s' % a['nickname'])
	self.introtext.body.set_text(' * Introduction:\n%s' % a['self_introduction'])
	self.sigtext.body.set_text(' * Signature:\n%s' % a['signature'])
	self.lasttext.body.set_text(' * Last usage: %s' % a['last_login_ip'])

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Query User",align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.idedit = urwid.Filler(urwid.Edit(caption=" * Enter ID: ", wrap='clip'))
        self.btnsearch = urwid.Filler(urwid.Button("Search", self.on_button_clicked))
        self.btncancel = urwid.Filler(urwid.Button("Cancel", self.on_button_clicked))

        self.buttoncolumn = urwid.Columns([('weight', 60, self.idedit), ('weight', 20, self.btnsearch),('weight',20,self.btncancel)])

	self.idtext = urwid.Filler(urwid.Text(' * ID: '))
	self.nicktext = urwid.Filler(urwid.Text(' * Nickname: '))
	self.introtext = urwid.Filler(urwid.Text(' * Introduction:\n'))
	self.sigtext = urwid.Filler(urwid.Text(' * Signature:\n'))
	self.lasttext = urwid.Filler(urwid.Text(' * Last usage:'))

	actiontext = urwid.Filler(urwid.Text(' * Press [Enter] to query another user, [q] to quit'))

        content = [('fixed',1, self.header), ('fixed',1,widget.blanktext),
            ('fixed',1,self.buttoncolumn), ('fixed',1,widget.dash),
            ('fixed',1,self.idtext), ('fixed',1,self.nicktext),
            ('fixed',6,self.introtext), ('fixed',6,self.sigtext),
            ('fixed',1,self.lasttext), ('fixed',1,widget.dash),
            actiontext,
            ]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_query_user().main()

# vim: set et ts=8 sw=4 sts=4:
