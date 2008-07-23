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

class ara_post_article(ara_forms):
    def __init__(self, session_key = None, board_name = None):
        self.board_name = board_name
        ara_forms.__init__(self, session_key)

    def get_current_board(self):
	return "garbages"

    def on_button_clicked(self, button):
        if button == self.btnokay:
            title = self.titleedit.body.get_edit_text()
            body = self.bodyedit.body.get_edit_text()
            print self.server.article_manager.write_article(self.session_key, self.board_name, {'title':title, 'content':body})
            # TODO: 서버와 통신하기
            pass
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

    def __initwidgets__(self, modify = False):
        if modify:
            self.header = urwid.Filler(urwid.Text(u"ARA: Modify Article  Current board: %s" % self.get_current_board(), align='center'))
	else:
            self.header = urwid.Filler(urwid.Text(u"ARA: Post Article  Current board: %s" % self.get_current_board(), align='center'))

        self.titleedit = urwid.Filler(urwid.Edit(caption="Title: ", wrap='clip'))
        bodytext = urwid.Filler(urwid.Text('Body'))
        self.bodyedit = urwid.Filler(urwid.Edit(multiline = True, wrap='clip'))

	self.chkinclude = urwid.CheckBox("Include in search")
	self.btnhelp = urwid.Button("Help", self.on_button_clicked)
	self.btnpreview = urwid.Button("Preview", self.on_button_clicked)
	self.btnokay = urwid.Button("OK", self.on_button_clicked)
	self.btncancel = urwid.Button("Cancel", self.on_button_clicked)

        self.bottomcolumn = urwid.Filler(urwid.Columns([('weight',40,self.chkinclude),('weight',15,self.btnhelp),('weight',15,self.btnpreview),('weight',15,self.btnokay),('weight',15,self.btncancel)]))

        content = [('fixed',1, self.header),('fixed',1,self.titleedit),('fixed',1,bodytext),('fixed',1,self.dash),self.bodyedit,('fixed',1,self.dash),('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_post_article().main()

# vim: set et ts=8 sw=4 sts=4:
