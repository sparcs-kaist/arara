#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_blacklist(ara_form):
    def keypress(self, size, key):
        self.mainpile.keypress(size, key)

    def on_button_clicked(self, button):
        if button == self.cancelbutton.body:
            self.parent.change_page("user_preferences", {'session_key':self.session_key})

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: My Blacklist",align='center'))

        self.okbutton = urwid.Filler(urwid.Button("OK", self.on_button_clicked))
        self.cancelbutton = urwid.Filler(urwid.Button("Cancel", self.on_button_clicked))
        buttoncolumn = widget.EasyColumn(self.okbutton, self.cancelbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',1,widget.dash),widget.blanktext, ('fixed',1,widget.dash),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_blacklist().main()

# vim: set et ts=8 sw=4 sts=4:
