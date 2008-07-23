#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *

class ara_read_article(ara_forms):
    def get_current_board(self):
	return "garbages"

    def __init__(self, session_key = None, board_name = None, article_id = None):
        self.board_name = board_name
        self.article_id = article_id
        ara_forms.__init__(self, session_key)

    def __initwidgets__(self):
        self.keymap = {
            'j': 'down',
            'k': 'up',
        }
        thread = self.server.article_manager.read(self.session_key, self.board_name, self.article_id)
        if thread[0]:
            body = thread[1][0]
            titletext = urwid.Filler(urwid.Text('Title: %s' % thread[1][0]['title']))
            infotext = urwid.Filler(urwid.Text('Author: %(id)s (%(nickname)s)    Hit: %(hit)s Reply: %(reply)s %(date)s' % {
                'id':thread[1][0]['author_username'], 'nickname':'peremen','hit':thread[1][0]['hit'],
                'reply':str(len(thread[1])-1),'date':thread[1][0]['date'].strftime("%Y/%m/%d %H:%M")}))
        else:
            pass
	self.header = urwid.Filler(urwid.Text(u"ARA: Read article",align='center'))
        functext = urwid.Filler(urwid.Text('(n)ext/(p)revious (b)lock (e)dit (d)elete (f)old/retract (r)eply (h)elp (q)uit'))

        content = [('fixed',1, self.header),('fixed',1,functext),('fixed',1,titletext),('fixed',1,infotext),('fixed',1,self.dash),self.blanktext]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_read_article().main()

# vim: set et ts=8 sw=4 sts=4:
