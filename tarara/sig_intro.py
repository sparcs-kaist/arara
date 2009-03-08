#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
from translation import _

class ara_sig_intro(ara_form):
    def keypress(self, size, key):
        self.mainpile.keypress(size, key)

    def on_button_clicked(self, button):
        retvalue = None
        if button == self.btnokay:
            self.myinfo['signature'] = self.sigedit.body.get_edit_text()
            self.myinfo['self_introduce'] = self.introedit.body.get_edit_text()
            try:
                retvalue =  self.server.member_manager.modify(self.session_key, self.myinfo)
                confirm = widget.Dialog(_('Sig/intro changed.'), [_('OK')], ('menu', 'bg', 'bgf'), 30, 5, self)
                self.overlay = confirm
                self.parent.run()
                if confirm.b_pressed == _('OK'):
                    self.parent.change_page("user_preferences",{'session_key':self.session_key})
                else:
                    pass
            except:
                    pass
        elif button == self.btncancel:
            self.parent.change_page("user_preferences",{'session_key':self.session_key})

    def set_sig_intro(self):
        self.sigedit.body.set_edit_text(self.myinfo['signature'])
        self.introedit.body.set_edit_text(self.myinfo['self_introduction'])

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(_('ARA: Change Introduction & Signature'), align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.myinfo = self.server.member_manager.get_info(self.session_key)

        sigtext = urwid.Filler(urwid.Text(_('Signature')))
        self.sigedit = urwid.Filler(urwid.Edit(wrap='clip'))
        introtext = urwid.Filler(urwid.Text(_('Introduction')))
        self.introedit = urwid.Filler(urwid.Edit(wrap='clip'))

	self.btnokay = urwid.Button(_('OK'), self.on_button_clicked)
	self.btncancel = urwid.Button(_('Cancel'), self.on_button_clicked)

        self.bottomcolumn = urwid.Filler(urwid.Columns([self.btnokay,self.btncancel]))

        content = [('fixed',1, self.header),
                ('fixed',1,sigtext),
                ('fixed',1,widget.dash),
                self.sigedit,
                ('fixed',1,widget.dash),
                ('fixed',1,introtext),
                ('fixed',1,widget.dash),
                self.introedit,
                ('fixed',1,widget.dash),
                ('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        self.set_sig_intro()

# vim: set et ts=8 sw=4 sts=4:
