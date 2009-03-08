#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
from translation import _

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
            try:
                title_content = {'title':title, 'content':body}
                if self.mode == 'modify':
                    result = self.server.article_manager.modify(self.session_key, self.board_name, self.article_id, **title_content)
                elif self.mode == 'reply':
                    result = self.server.article_manager.write_reply(self.session_key, self.board_name, self.article_id, **title_content)
                elif self.mode == 'post':
                    result = self.server.article_manager.write_article(self.session_key, self.board_name, **title_content)
                else:
                    return
                confirm = widget.Dialog(_('Article posted.'), [_('OK')], ('menu', 'bg', 'bgf'), 30, 5, self)
                self.overlay = confirm
                self.parent.run()
                if confirm.b_pressed == _('OK'):
                    self.parent.change_page("list_article",{'session_key':self.session_key, 'board_name':self.board_name})
            except:
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
            self.header = urwid.Filler(urwid.Text(_('ARA: Modify Article  Current board: %s') % self.board_name, align='center'))
        elif self.mode == 'reply':
            self.header = urwid.Filler(urwid.Text(_('ARA: Reply Article  Current board: %s') % self.board_name, align='center'))
	else:
            self.header = urwid.Filler(urwid.Text(_('ARA: Post Article  Current board: %s') % self.board_name, align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')

        self.titleedit = urwid.Filler(urwid.Edit(caption=_('Title: '), wrap='clip'))
        bodytext = urwid.Filler(urwid.Text(_('Body')))
        self.bodyedit = urwid.Filler(urwid.Edit(multiline = True, wrap='clip'))

	self.chkinclude = urwid.CheckBox(_('Include in search'))
	self.btnhelp = urwid.Button(_('Help'), self.on_button_clicked)
	self.btnpreview = urwid.Button(_('Preview'), self.on_button_clicked)
	self.btnokay = urwid.Button(_('OK'), self.on_button_clicked)
	self.btncancel = urwid.Button(_('Cancel'), self.on_button_clicked)

        self.bottomcolumn = urwid.Filler(urwid.Columns([
            ('weight',40,self.chkinclude),
            ('weight',15,self.btnokay),
            ('weight',15,self.btncancel),
            ('weight',15,self.btnhelp),
            ('weight',15,self.btnpreview),
            ]))

        content = [('fixed',1, self.header),
                ('fixed',1,self.titleedit),
                ('fixed',1,bodytext),
                ('fixed',1,widget.dash),
                self.bodyedit,
                ('fixed',1,widget.dash),
                ('fixed',1,self.bottomcolumn)]
        if self.mode == 'modify':
            original_article = self.server.article_manager.read(self.session_key, self.board_name, int(self.article_id))
            self.titleedit.body.set_edit_text(original_article[0]['title'])
            self.bodyedit.body.set_edit_text(original_article[0]['content'])
        elif self.mode == 'reply':
            original_article = self.server.article_manager.read(self.session_key, self.board_name, int(self.article_id))
            self.titleedit.body.set_edit_text("Re: " + original_article[0]['title'])

        self.mainpile = urwid.Pile(content)

# vim: set et ts=8 sw=4 sts=4:
