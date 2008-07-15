#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *

class ara_list_boards(ara_forms):
    def __initwidgets__(self):
        self.keymap = {
            'j': 'down',
            'k': 'up',
        }
        boardlist = self.server.article_manager.board_list(self.session_key)
        if boardlist[0] == False:
            # TODO: 폴백 위젯 구현
            return
	self.header = urwid.Filler(urwid.Text(u"ARA: List boards",align='center'))
        self.boardnameedit = urwid.Filler(urwid.Edit(caption=" * Enter board name: ", wrap='clip'))
        boardcounttext = urwid.Filler(urwid.Text(' * There are %s boards.' % len(boardlist[1].keys())))

        content = [('fixed',1, self.header),('fixed',1,self.boardnameedit),('fixed',1,boardcounttext),self.blanktext]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_list_boards(session_key = "e00bc932cc2d375075f443133ae0fa44").main()

# vim: set et ts=8 sw=4 sts=4:
