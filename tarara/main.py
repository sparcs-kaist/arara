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

class ara_main(object):
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

    def __init__(self):
        utf8decode = urwid.escape.utf8decode
        dash = urwid.SolidFill(utf8decode('─'))
        blank = urwid.SolidFill(u" ")
        blanktext = urwid.Filler(urwid.Text(' '))

	self.header = urwid.Filler(urwid.Text(u"ARA: Main Menu", align='center'))

        menuitems = [urwid.Text(' * '+ text) for text in menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

	self.tbtext = urwid.Filler(urwid.Text(u"Today Best", align='center'))
	tbitems = [urwid.Text("%(name)s (%(date)s)" % {"name":text[0], "date":text[1]}) for text in self.get_today_best()]
        self.tblist = urwid.ListBox(urwid.SimpleListWalker(tbitems))
	self.todaybest = urwid.Pile([('fixed',1,self.tbtext), self.tblist])

	self.wbtext = urwid.Filler(urwid.Text(u"Weekly Best", align='center'))
	wbitems = [urwid.Text("%(name)s (%(date)s)" % {"name":text[0], "date":text[1]}) for text in self.get_weekly_best()]
        self.wblist = urwid.ListBox(urwid.SimpleListWalker(wbitems))
	self.weeklybest = urwid.Pile([('fixed',1,self.wbtext), self.wblist])

	self.bests = urwid.Pile([self.todaybest, self.weeklybest])
	self.copyrightnotice = urwid.Filler(urwid.Text(
u"""  * Press [Tab] to jump between menu, today best, weekly best
 ARAra Release 1.0                                  Copyright © 2008, SPARCS"""))


        self.maincolumn = urwid.Columns([('weight',40,self.menulist),('weight',60,self.bests)])

        content = [('fixed',1, self.header),self.maincolumn,('fixed',2,self.copyrightnotice)]
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

ara_main().main()

# vim: set et ts=8 sw=4 sts=4
