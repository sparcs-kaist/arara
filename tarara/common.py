#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid

keymap = {
    'j': 'down',
    'k': 'up',
}

class ara_forms(object):
    def __init__(self):
        self.utf8decode = urwid.escape.utf8decode
        self.dash = urwid.SolidFill(self.utf8decode('─'))
        self.blank = urwid.SolidFill(u" ")
        self.blanktext = urwid.Filler(urwid.Text(' '))

	self.frame = self.__initwidgets__()

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
		if "window resize" in keys:
                    size = self.ui.get_cols_rows()
                self.frame.keypress(size, key)
   
    def draw_screen(self, size):
        canvas = self.frame.render(size, focus=True)
        self.ui.draw_screen(size, canvas)

# vim: set et ts=8 sw=4 sts=4
