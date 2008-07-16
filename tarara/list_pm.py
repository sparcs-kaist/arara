#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *
import listview

class pmlist_rowitem(FieldRow):
    fields = [
        ('new', 1, 'right'),
        ('number', 4, 'left'),
        ('author',12, 'left'),
        ('title',0, 'left'),
        ('date',5, 'left'),
    ]

class ara_list_pm(ara_forms):
    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Private message",align='center'))
        self.infotext = urwid.Filler(urwid.Text(" (N)ext/(P)revious Page (w)rite (B)lock (h)elp (q)uit"))

        itemlist = []
        itemlist += [{'new':'N', 'number':'1', 'author':'peremen','title':'text','date':'1/1'}]
        header = {'new':'N', 'number':'#', 'author':'Author', 'title':'Title', 'date':'Date'}

        boardlist = listview.get_view(itemlist, header, pmlist_rowitem)

        self.inboxbutton = urwid.Filler(urwid.Button("Inbox"))
        self.outboxbutton = urwid.Filler(urwid.Button("Outbox"))
        self.buttoncolumn = self._make_column(self.inboxbutton, self.outboxbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',1,self.infotext),('fixed',1,self.buttoncolumn),boardlist,]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_list_pm().main()

# vim: set et ts=8 sw=4 sts=4:
