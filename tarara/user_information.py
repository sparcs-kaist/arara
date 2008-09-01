#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
from translation import _

class ara_user_information(ara_form):
    menu = [
        _('List (c)onnected users'),
        _('Q(u)ery user'),
        _('(Q)uit menu'),
    ]
    menudesc = [
        _('Show information about\ncurrent users'),
        _('Query about user\'s last used\nIP, introduction, etc.'),
        _('Return to main menu'),
    ]

    def keypress(self, size, key):
        if key.lower() == 'c':
            self.menulist.set_focus(0)
            self.parent.change_page("list_connected_users", {'session_key':self.session_key})
        elif key.lower() == 'u':
            self.menulist.set_focus(1)
            self.parent.change_page("query_user", {'session_key':self.session_key, 'default_user':''})
        elif key.lower() == 'q':
            self.menulist.set_focus(2)
            self.parent.change_page("main", {'session_key':self.session_key})
        elif key == "enter":
            pos = self.menulist.get_focus()[1]
            if pos == 0:
                self.parent.change_page("list_connected_users", {'session_key':self.session_key})
            elif pos == 1:
                self.parent.change_page("query_user", {'session_key':self.session_key, 'default_user':''})
            elif pos == 2:
                self.parent.change_page("main", {'session_key':self.session_key})
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(_('ARA: User Information'), align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        menuitems = [widget.Item(" * "+w+"\n", None, 'selected') for w in self.menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

        menudescs = [widget.Item(w, None, 'selected') for w in self.menudesc]
        self.menudesclist = urwid.ListBox(urwid.SimpleListWalker(menudescs))

        self.maincolumn = urwid.Columns([('weight',40,self.menulist),('weight',60,self.menudesclist)])

        infotext = urwid.Filler(urwid.Text(_('  * Use [Tab] or arrow key to move each items')))

        content = [('fixed',1, self.header),('fixed',1,widget.blanktext),
                self.maincolumn,('fixed',1,widget.dash),
                ('fixed',1,infotext),]
        self.mainpile = urwid.Pile(content)

# vim: set et ts=8 sw=4 sts=4:
