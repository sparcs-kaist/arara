#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid

keymap = {
    'j': 'down',
    'k': 'up',
}

class ara_post(object):

    def __init__(self):
        utf8decode = urwid.escape.utf8decode
        dash = urwid.SolidFill(utf8decode('─'))
        blank = urwid.SolidFill(u" ")
        blanktext = urwid.Filler(urwid.Text(' '))

	self.header = urwid.Filler(urwid.Text(u"ARA: Change Introduction & Signature", align='center'))

        sigtext = urwid.Filler(urwid.Text('Signature'))
        sigedit = urwid.Filler(urwid.Edit(wrap='clip'))
        introtext = urwid.Filler(urwid.Text('Introduction'))
        introedit = urwid.Filler(urwid.Edit(wrap='clip'))

	self.btnokay = urwid.Button("OK")
	self.btncancel = urwid.Button("Cancel")

        self.bottomcolumn = urwid.Filler(urwid.Columns([self.btnokay,self.btncancel]))

        content = [('fixed',1, self.header),('fixed',1,sigtext),sigedit,('fixed',1,introtext),introedit,('fixed',1,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        self.frame = self.mainpile

    def main(self):
        self.ui = urwid.curses_display.Screen()
        self.ui.run_wrapper(self.run)

    def run(self):
        size = self.ui.get_cols_rows()
        quit = False
        while not quit:
            self.draw_screen(size)
            keys = self.ui.get_input()
            for key in keys:
                if key == 'tab':
                    quit = True
                    break
                if key in keymap:
                    key = keymap[key]
                self.frame.keypress(size, key)
   
    def draw_screen(self, size):
        canvas = self.frame.render(size, focus=True)
        self.ui.draw_screen(size, canvas)

ara_post().main()

# vim: set et ts=8 sw=4 sts=4
