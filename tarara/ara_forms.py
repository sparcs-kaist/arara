#!/usr/bin/python
# coding: utf-8

import xmlrpclib
import os
import urwid.curses_display
import urwid

class ara_forms(object):
    def __init__(self, session_key = None):
        self.utf8decode = urwid.escape.utf8decode
        self.dash = urwid.SolidFill(self.utf8decode('-'))
        self.blank = urwid.SolidFill(u" ")
        self.blanktext = urwid.Filler(urwid.Text(' '))
        self.keymap = {}
	self.server = xmlrpclib.Server("http://localhost:8000")
        self.session_key = session_key

	self.frame = self.__initwidgets__()

    def __keypress__(self, size, key):
	self.frame.keypress(size, key)

    def __resize__(self, size):
        pass

    def main(self):
        self.ui = urwid.curses_display.Screen()
        self.ui.register_palette([
            ('header', 'black', 'dark cyan', 'standout'),
            ('selected', 'default', 'light gray', 'bold'),
            ('reversed', 'white', 'black', 'bold'),
            ])
        self.ui.run_wrapper(self.run)

    def run(self):
        size = self.ui.get_cols_rows()
        self.quit = False
        while not self.quit:
            self.draw_screen(size)
            keys = self.ui.get_input()
            for key in keys:
                if key in self.keymap:
                    key = self.keymap[key]
		if "window resize" in keys:
                    size = self.ui.get_cols_rows()
                    self.__resize__(size)
                self.__keypress__(size, key)
   
    def draw_screen(self, size):
        canvas = self.frame.render(size, focus=True)
        self.ui.draw_screen(size, canvas)

    def update_session(self):
        if self.session_key != None:
            retvalue = self.server.update_session(self.session_key)
        return retvalue[0]

    def _make_column(self,widget1, widget2,ratio1=60, ratio2=40):
        return urwid.Columns([
            ('weight', ratio1, widget1),
            ('weight', ratio2, widget2),
            ])

# vim: set et ts=8 sw=4 sts=4:
