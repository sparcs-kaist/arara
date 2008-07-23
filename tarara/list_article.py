#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *
import listview

class articlelist_rowitem(FieldRow):
    fields = [
        ('new', 1, 'right'),
        ('number', 4, 'left'),
        ('author',12, 'left'),
        ('title',0, 'left'),
        ('date',5, 'left'),
        ('hit',7, 'left'),
        ('vote',4, 'left'),
    ]

class ara_list_article(ara_forms):
    def __init__(self, session_key = None, board_name = None):
        self.board_name = board_name
        ara_forms.__init__(self, session_key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Article list",align='center'))
        self.infotext1 = "(N)ext/(P)revious Page (n)ext/(p)revious article (Number+Enter) Jump to article"
        self.infotext2 = "(Enter,space) Read (w)rite (f)ind (/)Find next (?) Find previous (h)elp (q)uit"

        self.infotext1 = urwid.Filler(urwid.Text(self.infotext1))
        self.infotext2 = urwid.Filler(urwid.Text(self.infotext2))

        articlelist = self.server.article_manager.article_list(self.session_key, self.board_name)
        itemlist = []
        itemlist += [{'new':'N', 'number':'1', 'author':'peremen','title':'text','date':'1/1','hit':'100000','vote':'100'}]
        header = {'new':'N', 'number':'#', 'author':'Author', 'title':'Title', 'date':'Date', 'hit':'Hit', 'vote':'Vote'}

        boardlist = listview.get_view(itemlist, header, articlelist_rowitem)

        content = [('fixed',1, self.header),('fixed',1,self.infotext1),('fixed',1,self.infotext2),boardlist,]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_list_article().main()

# vim: set et ts=8 sw=4 sts=4:
