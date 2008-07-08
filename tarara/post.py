#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid

keymap = {
    'j': 'down',
    'k': 'up',
}
menu = [
    "(N)ew article",
    "(S)elect board",
    "(P)rivate message",
    "(U)ser preferences",
    "(H)elp",
    "(A)bout ARA",
    "(W)elcome screen",
    "(Q)uit",
]

class ara_post(object):
    def get_today_best(self):
        return [
            ["투베갑시다", "peremen"],
	    ["나도 투베가자","pipoket"],
	    ["꺼져라 내가 투베간다","ssaljalu"],
	    ["같이가요","jacob"],
	    ["메롱 약오르지","combacsa"],
	    ["랄라","kkhsoft"],
	]

    def get_weekly_best(self):
        return [
            ["투베갑시다", "peremen"],
	    ["나도 투베가자","pipoket"],
	    ["꺼져라 내가 투베간다","ssaljalu"],
	    ["같이가요","jacob"],
	    ["메롱 약오르지","combacsa"],
	    ["랄라","kkhsoft"],
	]
    def get_current_board(self):
	return "garbages"

    def __init__(self):
        utf8decode = urwid.escape.utf8decode
        dash = urwid.SolidFill(utf8decode('─'))
        blank = urwid.SolidFill(u" ")
        blanktext = urwid.Filler(urwid.Text(' '))

	self.header = urwid.Filler(urwid.Text(u"ARA: Post Article  Current board: %s" % self.get_current_board(), align='center'))

        titleedit = urwid.Filler(urwid.Edit(caption="Title: ", wrap='clip'))
        bodytext = urwid.Filler(urwid.Text('Body'))
        self.bodyedit = urwid.Filler(urwid.Edit(multiline = True, wrap='clip'))

	self.chkinclude = urwid.CheckBox("Include in search")
	self.btnhelp = urwid.Button("Help")
	self.btnpreview = urwid.Button("Preview")
	self.btnokay = urwid.Button("OK")
	self.btncancel = urwid.Button("Cancel")

        self.bottomcolumn = urwid.Filler(urwid.Columns([('weight',40,self.chkinclude),('weight',15,self.btnhelp),('weight',15,self.btnpreview),('weight',15,self.btnokay),('weight',15,self.btncancel)]))

        content = [('fixed',1, self.header),('fixed',1,titleedit),('fixed',1,bodytext),self.bodyedit,('fixed',1,self.bottomcolumn)]
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
