#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid

keymap = {
    'j': 'down',
    'k': 'up',
}

class ara_pm_read(object):
    def get_current_board(self):
	return "garbages"

    def __init__(self):
        utf8decode = urwid.escape.utf8decode
        dash = urwid.SolidFill(utf8decode('─'))
        blank = urwid.SolidFill(u" ")
        blanktext = urwid.Filler(urwid.Text(' '))

	self.header = urwid.Filler(urwid.Text(u"ARA: Read private message",align='center'))
        functext = urwid.Filler(urwid.Text('(n)ext/(p)revious (b)lock (d)elete (r)eply (h)elp (q)uit'))
	titletext = urwid.Filler(urwid.Text('Title: %s' % "윅베간다"))
	infotext = urwid.Filler(urwid.Text('Sender: %(id)s (%(nickname)s)     %(date)s' % {'id':'peremen', 'nickname':'peremen','date':'today'}))

        content = [('fixed',1, self.header),('fixed',1,functext),('fixed',1,titletext),('fixed',1,infotext),('fixed',1,dash),blanktext]
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

ara_pm_read().main()

# vim: set et ts=8 sw=4 sts=4
