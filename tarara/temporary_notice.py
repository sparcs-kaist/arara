#!/usr/bin/python
# coding: utf-8

import os
import socket
import urwid.curses_display
import urwid
from ara_form import *
import widget
from translation import _

class temporary_notice(ara_form):
    def keypress(self, size, key):
        if key.strip() == 'enter':
            sys.exit(0)
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
        message = u"""안녕하십니까. SPARCS입니다.

텔넷 아라는 현재 작업 중입니다.

다시 열리는 시기가 확정되는 대로 공지하겠습니다.

감사합니다.

[Enter] 키를 누르면 종료합니다."""
        self.message = urwid.Filler(urwid.Text(message, align='center'))
        self.mainpile = urwid.Pile([self.message])

# vim: set et ts=8 sw=4 sts=4:
