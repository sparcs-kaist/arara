#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_helpviewer(ara_form):
    def __init__(self, parent, session_key = None, topic= "", caller="main",caller_args ={}):
        self.topic = topic
        self.caller = caller
        self.caller_args = {}
        ara_form.__init__(self, parent, session_key)

    def keypress(self, size, key):
        if "enter" in key:
            self.parent.change_page(self.caller, self.caller_args)

    def __initwidgets__(self):
        self.toptext = urwid.Filler(urwid.Text("Help: %s" % self.topic, align='center'))
        self.toptext = urwid.AttrWrap(self.toptext, 'reversed')

        basedir = os.path.dirname(__file__)
        help = os.path.join(basedir+"/help", self.topic + '.txt')
        f = open(help, 'r')
        content = f.read().decode('utf-8')
        content = urwid.Filler(urwid.Text(content))

        self.entertext = urwid.Filler(urwid.Text("Press [Enter] key to return"))

        content = [self.banner,('fixed',1, self.toptext),content, ("fixed", 1, self.entertext)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_welcome().main()

# vim: set et ts=8 sw=4 sts=4:
