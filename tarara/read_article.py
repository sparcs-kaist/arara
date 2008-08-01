#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
from string import Template

class ara_read_article(ara_form):
    def keypress(self, size, key):
        key = key.strip()
        if key == 'e':
            self.parent.change_page("post_article", {'session_key':self.session_key, 'board_name':self.board_name, 'mode':'modify', 'article_id':self.article_id})
        elif key == 'r':
            self.parent.change_page("post_article", {'session_key':self.session_key, 'board_name':self.board_name, 'mode':'reply', 'article_id':self.article_id})
        elif key == 'q':
            self.parent.change_page("list_article", {'session_key':self.session_key, 'board_name':self.board_name})
        elif key == 'v':
            retvalue = self.server.article_manager.vote_article(self.session_key, self.board_name, self.article_id)
            if retvalue[0]:
                confirm = widget.Dialog("Voted.", ["OK"], ('menu', 'bg', 'bgf'), 30, 5, self)
            else:
                confirm = widget.Dialog(retvalue[1], ["OK"], ('menu', 'bg', 'bgf'), 30, 5, self)
            self.overlay = confirm
            self.parent.run()
            self.overlay = None
            self.set_article(board_name = self.board_name, article_id = self.article_id)
        else:
            self.mainpile.keypress(size, key)

    def __init__(self, parent, session_key = None, board_name = None, article_id = None):
        self.board_name = board_name
        self.article_id = article_id
        self.title_template = Template("Title: ${TITLE}")
        self.author_template = Template("Author: ${AUTHOR} (${NICKNAME})")
        self.info_template = Template("Date: ${DATE} Hit: ${HIT} Reply: ${REPLY} Vote: ${VOTE}")
        self.reply_template = Template("Reply by ${AUTHOR}(${NICKNAME}) on ${DATE} ${NEW}")
        ara_form.__init__(self, parent, session_key)

    def set_article(self, board_name, article_id):
        thread = self.server.article_manager.read(self.session_key, board_name, article_id)
        if thread[0]:
            body = thread[1][0]
            self.titletext.body.set_text(self.title_template.safe_substitute(
                TITLE=body['title']))
            self.authortext.body.set_text(self.author_template.safe_substitute(
                AUTHOR=body['author_username'], NICKNAME='blahblah'))
            self.infotext.body.set_text(self.info_template.safe_substitute(
                HIT=body['hit'], REPLY=str(len(thread[1])-1), 
                DATE=body['date'].strftime("%Y/%m/%d %H:%M"), VOTE=str(body['vote'])))
            self.articletext.body.set_text(body['content'])

    def __initwidgets__(self):
        self.keymap = {
            'j': 'down',
            'k': 'up',
        }
        self.titletext = urwid.Filler(urwid.Text(''))
        self.authortext = urwid.Filler(urwid.Text(''))
        self.infotext = urwid.Filler(urwid.Text(''))
        self.articletext = urwid.Filler(urwid.Text(''))
        self.set_article(self.board_name, self.article_id)
	self.header = urwid.Filler(urwid.Text(u"ARA: Read article",align='center'))
        functext = urwid.Filler(urwid.Text('(n)ext/(p)revious (b)lock (e)dit (d)elete (f)old/retract (r)eply (v)ote (q)uit'))

        content = [('fixed',1,self.authortext),('fixed',1,self.infotext),
                ('fixed',1,self.titletext),
                ('fixed',1,widget.dash),self.articletext,
                ('fixed',1,urwid.AttrWrap(functext, 'reversed'))]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_read_article().main()

# vim: set et ts=8 sw=4 sts=4:
