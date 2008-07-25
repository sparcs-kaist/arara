#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *

class ara_write_pm(ara_forms):
    def __init__(self, session_key = None, mode='write', reply_to = ""):
        self.mode = mode
        self.reply_to = reply_to
        ara_forms.__init__(self, session_key)

    def on_button_clicked(self, button):
        if button == self.btnokay:
            to = self.idedit.get_edit_text()
            to = [x.strip() for x in to.split(';')]
            body = self.bodyedit.body.get_edit_text()
            for sender in to:
                print self.server.messaging_manager.send_message(self.session_key, sender, body)
        elif button == self.btncancel:
            # TODO: 이전 화면으로 돌아가기
            pass
        elif button == self.btnhelp:
            # TODO: 편집 도움말
            pass
        elif button == self.btnpreview:
            # TODO: 미리보기
            pass
        else:
            assert("Call for undefined button")
    def __initwidgets__(self):
        self.idedit = urwid.Edit(caption="To (Enter ID): ", wrap='clip')
        if self.mode == 'reply':
            header = urwid.Filler(urwid.Text(u"ARA: Reply private message", align='center'))
            self.idedit.set_edit_text(self.reply_to)
        elif self.mode == 'write':
            header = urwid.Filler(urwid.Text(u"ARA: Write private message", align='center'))

	self.btnsearch = urwid.Button("Search by nickname")
        self.idcolumn = urwid.Filler(urwid.Columns([('weight',60,self.idedit),('weight',40,self.btnsearch)]))
	self.info = urwid.Filler(urwid.Text(u"* You can use semicolon(;) to send two or more person."))

        bodytext = urwid.Filler(urwid.Text('Body'))
        self.bodyedit = urwid.Filler(urwid.Edit(multiline = True, wrap='clip'))

	self.btnhelp = urwid.Button("Help", self.on_button_clicked)
	self.btnpreview = urwid.Button("Preview", self.on_button_clicked)
	self.btnokay = urwid.Button("Send", self.on_button_clicked)
	self.btncancel = urwid.Button("Cancel", self.on_button_clicked)

        self.bottomcolumn = urwid.Filler(urwid.Columns([
            ('weight',40,urwid.Text(' ')),
            ('weight',15,self.btnhelp),
            ('weight',15,self.btnpreview),
            ('weight',15,self.btnokay),
            ('weight',15,self.btncancel)]))

        content = [('fixed',1, header),
                ('fixed',1,self.idcolumn),
                ('fixed',1,self.info),
                ('fixed',1,bodytext),
                ('fixed',1,self.dash),
                self.bodyedit,
                ('fixed',1,self.dash),
                ('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_write_pm().main()

# vim: set et ts=8 sw=4 sts=4:
