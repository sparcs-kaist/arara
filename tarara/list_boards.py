#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
import listview
from translation import _

class boardlist_rowitem(widget.FieldRow):
    fields = [
        ('name',12, 'left'),
        ('desc',0, 'left'),
    ]

class ara_list_boards(ara_form):
    def keypress(self, size, key):
        mainpile_focus = self.mainpile.get_focus()
        if mainpile_focus == self.boardlist:
            if key == "enter":
                # self.boardlist.get_body().get_focus()[0].w.w.widget_list : 현재 활성화된 항목
                boardname = self.boardlist.get_body().get_focus()[0].w.w.widget_list[0].get_text()[0]
                self.parent.change_page("list_article", {'session_key':self.session_key, 'board_name':boardname})
            else:
                self.mainpile.keypress(size, key)
        elif mainpile_focus == self.boardnameedit:
            if key == 'enter':
                boardname = self.boardnameedit.body.get_edit_text()
                try:
                    status = self.server.board_manager.get_board(boardname)
                    self.parent.change_page("list_article", {'session_key':self.session_key, 'board_name':boardname})
                except InvalidOperation, e:
                    confirm = widget.Dialog(_('No such board. Returning to main menu.'), [_('Ok')], ('menu', 'bg', 'bgf'), 30, 6, self)
                    self.overlay = confirm
                    self.parent.run()
                    self.parent.change_page('main', {'session_key':self.session_key})
            else:
                self.mainpile.keypress(size, key)
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
        self.keymap = {
            'j': 'down',
            'k': 'up',
        }
        boardlist = self.server.board_manager.get_board_list()

	self.header = urwid.Filler(urwid.Text(_('ARA: List boards'),align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.boardnameedit = urwid.Filler(urwid.Edit(caption=_(' * Enter board name: '), wrap='clip'))
        itemlist = []
        if len(boardlist) > 0:
            boardcounttext = urwid.Filler(urwid.Text(_(' * There are %s boards.') % len(boardlist)))
            for data in boardlist:
                itemlist += [{'name':data.board_name, 'desc':data.board_description}]
        else:
            boardcounttext = urwid.Filler(urwid.Text(_(' * No boards found. Have a nice day.')))
            itemlist = [{'name':'', 'desc':_('No boards found. Have a nice day.')}]

        header = {'name':_('Name'), 'desc':_('Description')}
        self.boardlist = listview.get_view(itemlist, header, boardlist_rowitem)

        content = [('fixed',1, self.header),('fixed',1,self.boardnameedit),('fixed',1,boardcounttext),self.boardlist]
        self.mainpile = urwid.Pile(content)

# vim: set et ts=8 sw=4 sts=4:
