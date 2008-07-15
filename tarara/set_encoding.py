#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *

class ara_set_encoding(ara_forms):
    def __initwidgets__(self):
        self.keymap = {
            'j': 'down',
            'k': 'up',
        }
	self.header = urwid.Filler(urwid.Text(u"ARA: Set Terminal Encoding",align='center'))
        self.infotext =urwid.Filler(urwid.Text(""" * Select new encoding from below.
   If your terminal encoding isn't supported, please contact sysop."""))

        encitems = ['CP949 (Default for Korean Windows)','UTF-8 (Default for most Linux)','Big5 (Default for Chinese Windows)']
        encitems = [Item(w, None, 'selected') for w in encitems]
        self.enclist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(encitems)))

        okbutton = urwid.Filler(urwid.Button("OK"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(okbutton, cancelbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',2,self.infotext),self.enclist,('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_set_encoding().main()

# vim: set et ts=8 sw=4 sts=4:
