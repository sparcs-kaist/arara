#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_write_pm(ara_form):
    def __init__(self, parent, session_key = None, mode='write', reply_to = ""):
        self.mode = mode
        self.reply_to = reply_to
        ara_form.__init__(self, parent, session_key)

    def keypress(self, size, key):
        self.mainpile.keypress(size, key)

    def on_button_clicked(self, button):
        sended = True
        retvalue = None
        if button == self.btnokay:
            to = self.idedit.get_edit_text()
            to = [x.strip() for x in to.split(';')]
            body = self.bodyedit.body.get_edit_text()
            for sender in to:
                retvaule = self.server.messaging_manager.send_message(self.session_key, sender, body)
                sended = sended & retvalue[0]
                if sended:
                    confirm = widget.Dialog("Message sent.", ["OK"], ('menu', 'bg', 'bgf'), 30, 5, self)
                    self.overlay = confirm
                    self.parent.run()
                    if confirm.b_pressed == "OK":
                        self.parent.change_page("user_preferences",{'session_key':self.session_key})
                    else:
                        pass

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
            ('weight',15,self.btnokay),
            ('weight',15,self.btncancel),
            ('weight',15,self.btnhelp),
            ('weight',15,self.btnpreview),
            ]))

        content = [('fixed',1, header),
                ('fixed',1,self.idcolumn),
                ('fixed',1,self.info),
                ('fixed',1,bodytext),
                ('fixed',1,widget.dash),
                self.bodyedit,
                ('fixed',1,widget.dash),
                ('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_write_pm().main()

# vim: set et ts=8 sw=4 sts=4:
