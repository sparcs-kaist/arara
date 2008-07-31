#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_post_article(ara_form):
    def __init__(self, parent, session_key = None, board_name = None, mode='post', article_id = 0):
        self.board_name = board_name
        self.mode= mode
        self.article_id = article_id
        ara_form.__init__(self, parent, session_key)

    def keypress(self, size, key):
        self.mainpile.keypress(size, key)

    def on_button_clicked(self, button):
        if button == self.btnokay:
            retvalue = None
            title = self.titleedit.body.get_edit_text()
            body = self.bodyedit.body.get_edit_text()
            if self.mode == 'modify':
                retvalue= self.server.article_manager.modify(self.session_key, self.board_name, self.article_id, {'title':title, 'content':body})
            elif self.mode == 'reply':
                retvalue= self.server.article_manager.write_reply(self.session_key, self.board_name, self.article_id, {'title':title, 'content':body})
            elif self.mode == 'post':
                retvalue= self.server.article_manager.write_article(self.session_key, self.board_name, {'title':title, 'content':body})
            else:
                pass
            if retvalue[0] == True:
                confirm = widget.Dialog("Article posted.", ["OK"], ('menu', 'bg', 'bgf'), 30, 5, self)
                self.overlay = confirm
                self.parent.run()
                if confirm.b_pressed == "OK":
                    self.parent.change_page("list_article",{'session_key':self.session_key, 'board_name':self.board_name})
            else:
                #self.overlay = None
                #self.parent.run()
                pass
        elif button == self.btncancel:
            self.parent.change_page("list_article",{'session_key':self.session_key, 'board_name':self.board_name})
        elif button == self.btnhelp:
            # TODO: 편집 도움말
            pass
        elif button == self.btnpreview:
            # TODO: 미리보기
            pass
        else:
            assert("Call for undefined button")

    def __initwidgets__(self):
        if self.mode == 'modify':
            self.header = urwid.Filler(urwid.Text(u"ARA: Modify Article  Current board: %s" % self.board_name, align='center'))
        elif self.mode == 'reply':
            self.header = urwid.Filler(urwid.Text(u"ARA: Reply Article  Current board: %s" % self.board_name, align='center'))
	else:
            self.header = urwid.Filler(urwid.Text(u"ARA: Post Article  Current board: %s" % self.board_name, align='center'))

        self.titleedit = urwid.Filler(urwid.Edit(caption="Title: ", wrap='clip'))
        bodytext = urwid.Filler(urwid.Text('Body'))
        self.bodyedit = urwid.Filler(urwid.Edit(multiline = True, wrap='clip'))

	self.chkinclude = urwid.CheckBox("Include in search")
	self.btnhelp = urwid.Button("Help", self.on_button_clicked)
	self.btnpreview = urwid.Button("Preview", self.on_button_clicked)
	self.btnokay = urwid.Button("OK", self.on_button_clicked)
	self.btncancel = urwid.Button("Cancel", self.on_button_clicked)

        self.bottomcolumn = urwid.Filler(urwid.Columns([
            ('weight',40,self.chkinclude),
            ('weight',15,self.btnhelp),
            ('weight',15,self.btnpreview),
            ('weight',15,self.btnokay),
            ('weight',15,self.btncancel)]))

        content = [('fixed',1, self.header),
                ('fixed',1,self.titleedit),
                ('fixed',1,bodytext),
                ('fixed',1,widget.dash),
                self.bodyedit,
                ('fixed',1,widget.dash),
                ('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_post_article().main()

# vim: set et ts=8 sw=4 sts=4:
