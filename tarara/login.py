#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from common import *

class ara_login(ara_forms):
    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def __keypress__(self, size, key):
        self.langlist.get_w().set_focus(1)
        if key.strip() == 'tab':
            curfocus = self.bottomcolumn.get_focus_column()
            self.bottomcolumn.set_focus_column((curfocus + 1) % 3)
        elif key.strip() == 'enter':
            pass
        else:
            self.frame.keypress(size, key)

    def __initwidgets__(self):
        self.message = urwid.Filler(urwid.Text(self.get_login_message(), align="center"))
        self.message_ko = urwid.Filler(urwid.Text(u"[Tab] 키를 누르면 항목간을 전환할 수 있습니다", align='center'))
        self.message_en = urwid.Filler(urwid.Text(u"Press [Tab] key to jump between each items", align='center'))

        idedit = urwid.Filler(urwid.Edit(caption="ID:", wrap='clip'))
        pwedit = urwid.Filler(urwid.Edit(caption="Password:", wrap='clip'))
        self.idpwpile = urwid.Pile([idedit, pwedit])

        langitems = [urwid.Text('Korean'), urwid.Text('English'), urwid.Text('Chinese')]
        self.langlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(langitems)))

        joinitems = [urwid.Text('Join'), urwid.Text('Guest')]
        self.joinlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(joinitems)))

        self.bottomcolumn = urwid.Columns([('weight',40,self.idpwpile),('weight',30,self.langlist),('weight',30,self.joinlist)])

        content = [self.message,('fixed',1, self.dash), ("fixed", 1, self.message_ko), ('fixed',1,self.message_en), ('fixed',1,self.blank), ('fixed',4,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        self.keymap = {'left':'', 'right':''}
	return self.mainpile

ara_login().main()

# vim: set et ts=8 sw=4 sts=4:
