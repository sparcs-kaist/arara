#!/usr/bin/python
# coding: utf-8

import urwid
import urwid.raw_display
from temporary_notice import *

Screen = urwid.raw_display.Screen

class ara_display:
    palette = ([
        ('header', 'black', 'dark cyan', 'bold'),
        ('selected', 'black', 'light gray', 'standout'),
        ('reversed', 'black', 'light gray', 'bold'),
        ('article_selected', 'white', 'dark red', 'bold'),
        ('menu', 'default', 'default', 'standout'),
        ('bg', 'default', 'default'),
        ('bgf', 'light gray', 'dark blue', 'standout'),
        ])
    def __init__(self):
        self.ara_login = temporary_notice(self)
        pass

    def change_page(self, pagename, args):
        if pagename == "temporary_notice":
            self.view = self.ara_login

    def main(self):
        self.ui = Screen()
        self.ui.register_palette(self.palette)
        self.change_page("temporary_notice",{})
        self.ui.run_wrapper(self.run)

    def run(self):
        self.size = self.ui.get_cols_rows()
        while True:
            #self.view = self.ara_login
            if self.view.overlay:
                canvas = self.view.overlay.render(self.size, focus = 1)
            else:
                canvas = self.view.render(self.size, focus = 1)
            self.ui.draw_screen(self.size, canvas)
            keys = None
            while not keys:
                keys = self.ui.get_input()
                for k in keys:
                    if k =='window resize':
                        self.size = self.ui.get_cols_rows()
                    if self.view.overlay:
                        k = self.view.overlay.keypress(self.size, k)
                        if self.view.overlay.quit:
                            return
                    else:
                        k = self.view.keypress(self.size, k)

if __name__ == "__main__":
    ara_display().main()
# vim: set et ts=8 sw=4 sts=4:


