#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from string import Template

class ara_read_article(ara_forms):
    def get_current_board(self):
	return "garbages"

    def __init__(self, session_key = None, board_name = None, article_id = None):
        self.board_name = board_name
        self.article_id = article_id
        self.title_template = Template("Title: ${TITLE}")
        self.info_template = Template("Author: ${AUTHOR}(${NICKNAME})    Hit: ${HIT} Reply: ${REPLY} ${DATE}")
        self.reply_template = Template("Reply by ${AUTHOR}(${NICKNAME}) on ${DATE} ${NEW}")
        ara_forms.__init__(self, session_key)

    def set_article(self, board_name, article_id):
        thread = self.server.article_manager.read(self.session_key, board_name, article_id)
        if thread[0]:
            body = thread[1][0]
            self.titletext.body.set_text(self.title_template.safe_substitute(TITLE=body['title']))
            self.infotext.body.set_text(self.info_template.safe_substitute(AUTHOR=body['author_username'],
                NICKNAME='blahblah', HIT=body['hit'], REPLY=str(len(thread[1])-1),
                DATE=body['date'].strftime("%Y/%m/%d %H:%M")))

    def __initwidgets__(self):
        self.keymap = {
            'j': 'down',
            'k': 'up',
        }
        self.titletext = urwid.Filler(urwid.Text(''))
        self.infotext = urwid.Filler(urwid.Text(''))
        self.set_article(self.board_name, self.article_id)
	self.header = urwid.Filler(urwid.Text(u"ARA: Read article",align='center'))
        functext = urwid.Filler(urwid.Text('(n)ext/(p)revious (b)lock (e)dit (d)elete (f)old/retract (r)eply (h)elp (q)uit'))

        content = [('fixed',1, self.header),('fixed',1,functext),('fixed',1,self.titletext),('fixed',1,self.infotext),('fixed',1,self.dash),self.blanktext]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_read_article().main()

# vim: set et ts=8 sw=4 sts=4:
