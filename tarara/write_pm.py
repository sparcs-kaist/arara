#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
from translation import _

class ara_write_pm(ara_form):
    def __init__(self, parent, session_key = None, mode='write', reply_to = ""):
        self.mode = mode
        self.reply_to = reply_to
        ara_form.__init__(self, parent, session_key)

    def keypress(self, size, key):
        self.mainpile.keypress(size, key)

    def on_button_clicked(self, button):
        retvalue = None
        if button == self.btnokay:
            to = self.idedit.get_edit_text()
            body = self.bodyedit.body.get_edit_text()
            retvalue = self.server.messaging_manager.send_message(self.session_key, to, body)
            if retvalue[0]:
                confirm = widget.Dialog(_('Message sent.'), [_('OK')], ('menu', 'bg', 'bgf'), 30, 5, self)
                self.overlay = confirm
                self.parent.run()
                self.parent.change_page("list_pm",{'session_key':self.session_key})

        elif button == self.btncancel:
            self.parent.change_page("list_pm", {'session_key':self.session_key})
        elif button == self.btnhelp:
            # TODO: 편집 도움말
            pass
        elif button == self.btnpreview:
            # TODO: 미리보기
            pass
        else:
            assert("Call for undefined button")

    def __initwidgets__(self):
        self.idedit = urwid.Edit(caption=_('To (Enter ID): '), wrap='clip')
        if self.mode == 'reply':
            header = urwid.Filler(urwid.Text(_('ARA: Reply private message'), align='center'))
            self.idedit.set_edit_text(self.reply_to)
        elif self.mode == 'write':
            header = urwid.Filler(urwid.Text(_('ARA: Write private message'), align='center'))

	self.btnsearch = urwid.Button(_('Search by nickname'))
        self.idcolumn = urwid.Filler(urwid.Columns([('weight',60,self.idedit),('weight',40,self.btnsearch)]))

        bodytext = urwid.Filler(urwid.Text(_('Body')))
        self.bodyedit = urwid.Filler(urwid.Edit(multiline = True, wrap='clip'))

	self.btnhelp = urwid.Button(_('Help'), self.on_button_clicked)
	self.btnpreview = urwid.Button(_('Preview'), self.on_button_clicked)
	self.btnokay = urwid.Button(_('Send'), self.on_button_clicked)
	self.btncancel = urwid.Button(_('Cancel'), self.on_button_clicked)

        self.bottomcolumn = urwid.Filler(urwid.Columns([
            ('weight',40,urwid.Text(' ')),
            ('weight',15,self.btnokay),
            ('weight',15,self.btncancel),
            ('weight',15,self.btnhelp),
            ('weight',15,self.btnpreview),
            ]))

        content = [('fixed',1, header),
                ('fixed',1,self.idcolumn),
                ('fixed',1,bodytext),
                ('fixed',1,widget.dash),
                self.bodyedit,
                ('fixed',1,widget.dash),
                ('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

# vim: set et ts=8 sw=4 sts=4:
