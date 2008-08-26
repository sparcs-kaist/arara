#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_query_user(ara_form):
    def __init__(self, parent, session_key = None, default_user = ''):
        self.default_user = default_user
        ara_form.__init__(self, parent, session_key)

    def keypress(self, size, key):
        if key == 'tab':
            buttoncolumnfocus = self.buttoncolumn.get_focus()
            if buttoncolumnfocus == self.idedit:
                self.buttoncolumn.set_focus(self.btnsearch)
            elif buttoncolumnfocus == self.btnsearch:
                self.buttoncolumn.set_focus(self.btncancel)
            elif buttoncolumnfocus == self.btncancel:
                self.buttoncolumn.set_focus(self.idedit)
        elif key == 'shift tab':
            buttoncolumnfocus = self.buttoncolumn.get_focus()
            if buttoncolumnfocus == self.idedit:
                self.buttoncolumn.set_focus(self.btncancel)
            elif buttoncolumnfocus == self.btncancel:
                self.buttoncolumn.set_focus(self.btnsearch)
            elif buttoncolumnfocus == self.btnsearch:
                self.buttoncolumn.set_focus(self.idedit)
        elif 'enter' in key and self.buttoncolumn.get_focus() == self.idedit:
            edittext = self.idedit.body.get_edit_text().strip()
            if edittext != '':
                self.query_information(edittext)
        else:
            self.mainpile.keypress(size, key)

    def on_button_clicked(self, button):
        if button == self.btnsearch.body:
            self.query_information(self.idedit.body.get_edit_text())
        elif button == self.btncancel.body:
            self.parent.change_page("user_information", {'session_key':self.session_key})

    def query_information(self, id):
        retvalue, data = self.server.member_manager.query_by_username(self.session_key, id)
        if retvalue:
            self.idtext.body.set_text(' * ID: %s' % data['username'])
            self.nicktext.body.set_text(' * Nickname: %s' % data['nickname'])
            self.introtext.body.set_text(' * Introduction:\n%s' % data['self_introduction'])
            self.sigtext.body.set_text(' * Signature:\n%s' % data['signature'])
            self.lasttext.body.set_text(' * Last usage: %s' % data['last_login_ip'])
        else:
            self.idtext.body.set_text(data)
            self.nicktext.body.set_text('')
            self.introtext.body.set_text('')
            self.sigtext.body.set_text('')
            self.lasttext.body.set_text('')

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Query User",align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.idedit = urwid.Filler(urwid.Edit(caption=" * Enter ID: ", wrap='clip'))
        self.idedit.body.set_edit_text(self.default_user)
        self.btnsearch = urwid.Filler(urwid.Button("Search", self.on_button_clicked))
        self.btncancel = urwid.Filler(urwid.Button("Cancel", self.on_button_clicked))

        self.buttoncolumn = urwid.Columns([('weight', 60, self.idedit), ('weight', 20, self.btnsearch),('weight',20,self.btncancel)])

	self.idtext = urwid.Filler(urwid.Text(''))
	self.nicktext = urwid.Filler(urwid.Text(''))
	self.introtext = urwid.Filler(urwid.Text(''))
	self.sigtext = urwid.Filler(urwid.Text(''))
	self.lasttext = urwid.Filler(urwid.Text(''))

	actiontext = urwid.Filler(urwid.Text(' * Enter user ID and press [Search]'))

        content = [('fixed',1, self.header), ('fixed',1,widget.blanktext),
            ('fixed',1,self.buttoncolumn), ('fixed',1,widget.dash),
            ('fixed',1,self.idtext), ('fixed',1,self.nicktext),
            ('fixed',6,self.introtext), self.sigtext,
            ('fixed',1,self.lasttext), ('fixed',1,widget.dash),
            ('fixed',1,actiontext),
            ]
        self.mainpile = urwid.Pile(content)
        if self.default_user != '':
            self.query_information(self.idedit.body.get_edit_text())

if __name__=="__main__":
    ara_query_user().main()

# vim: set et ts=8 sw=4 sts=4:
