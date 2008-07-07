#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid

keymap = {
    'j': 'down',
    'k': 'up',
}

class ara_toc(object):
    def get_banner(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'banner.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def get_ip(self):
        return "127.0.0.1"

    def get_location(self):
        return "Web"

    def get_date(self):
        return "Today"

    def __init__(self):
        utf8decode = urwid.escape.utf8decode
        dash = urwid.SolidFill(utf8decode('─'))
        blank = urwid.SolidFill(u" ")
        blanktext = urwid.Filler(urwid.Text(' '))
        self.banner = urwid.Filler(urwid.Text(self.get_banner()))

        logintext = "Last login: %(IP)s/%(location)s at %(date)s"
        logindata = {"IP": self.get_ip(), "location": self.get_location(), "date":self.get_date()}
        self.logininfo = urwid.Filler(urwid.Text(logintext % logindata))

        self.entertext = urwid.Filler(urwid.Text("Press [Enter] key to continue"))

        content = [self.banner,('fixed',1, self.logininfo),('fixed',1,blank), ("fixed", 1, self.entertext)]
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
                if key == 'enter':
                    quit = True
                    break
                if key in keymap:
                    key = keymap[key]
                self.frame.keypress(size, key)
   
    def draw_screen(self, size):
        canvas = self.frame.render(size, focus=True)
        self.ui.draw_screen(size, canvas)

ara_toc().main()

# vim: set et ts=8 sw=4 sts=4
