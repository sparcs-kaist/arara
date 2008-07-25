#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *
import listview
from write_pm import *

class pmlist_rowitem(FieldRow):
    fields = [
        ('new', 1, 'right'),
        ('number', 4, 'left'),
        ('author',12, 'left'),
        ('title',0, 'left'),
        ('date',5, 'left'),
    ]

class ara_list_pm(ara_forms):
    def display_inbox(self):
        self.list_header = {'new':'N', 'number':'#', 'author':'Author', 'title':'Title', 'date':'Date'}
        self.pmlist.set_header(listview.make_header(self.list_header, pmlist_rowitem))

        message_list = self.server.messaging_manager.receive_list(self.session_key, 1, 10)
        message_item = []
        if len(message_list[1]) == 1:
            message_item = [{'new':'', 'number':'', 'author':'','title':'No private messages. Have a nice day.','date':''}]
        else:
            for msg in message_list[1]:
                if msg.has_key("last_page"):
                    continue
                message_item += [{'new':str(msg['read_status']), 'number':str(msg['id']), 'author':msg['from'], 'title':msg['message'], 'date':msg['sent_time'].strftime("%m/%d")}]
        self.pmlist.set_body(listview.make_body(message_item, pmlist_rowitem))

    def display_outbox(self):
        self.list_header = {'new':'N', 'number':'#', 'author':'Recepient', 'title':'Title', 'date':'Date'}
        self.pmlist.set_header(listview.make_header(self.list_header, pmlist_rowitem))

        message_list = self.server.messaging_manager.sent_list(self.session_key, 1, 10)
        message_item = []
        if len(message_list[1]) == 1:
            message_item = [{'new':'', 'number':'', 'author':'','title':'No private messages. Have a nice day.','date':''}]
        else:
            for msg in message_list[1]:
                if msg.has_key("last_page"):
                    continue
                message_item += [{'new':str(msg['read_status']), 'number':str(msg['id']), 'author':msg['to'], 'title':msg['message'], 'date':msg['sent_time'].strftime("%m/%d")}]
        self.pmlist.set_body(listview.make_body(message_item, pmlist_rowitem))

    def __keypress__(self, size, key):
        key = key.strip()
        mainpile_focus = self.mainpile.get_focus()
        if key == 'w':
            ara_write_pm(self.session_key, 'write').main()
        elif key == 'r':
            ara_write_pm(self.session_key, 'reply', 'me').main()
        elif mainpile_focus == self.pmlist and key=='enter':
            pm_id = int(self.pmlist.get_body().get_focus()[0].w.w.widget_list[1].get_text()[0])
        else:
            self.frame.keypress(size, key)

    def on_button_pressed(self, button):
        if button == self.inboxbutton.body:
            self.display_inbox()
        elif button == self.outboxbutton.body:
            self.display_outbox()

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Private message",align='center'))
        self.infotext = urwid.Filler(urwid.Text(" (N)ext/(P)revious Page (w)rite (B)lock (h)elp (q)uit"))

        itemlist = []
        itemlist += [{'new':'N', 'number':'1', 'author':'peremen','title':'text','date':'1/1'}]
        self.list_header = {'new':'N', 'number':'#', 'author':'Author', 'title':'Title', 'date':'Date'}

        self.pmlist = listview.get_view(itemlist, self.list_header, pmlist_rowitem)

        self.inboxbutton = urwid.Filler(urwid.Button("Inbox", self.on_button_pressed))
        self.outboxbutton = urwid.Filler(urwid.Button("Outbox", self.on_button_pressed))
        self.buttoncolumn = self._make_column(self.inboxbutton, self.outboxbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',1,self.infotext),('fixed',1,self.buttoncolumn),self.pmlist,]
        self.mainpile = urwid.Pile(content)

        self.display_inbox()

        return self.mainpile

if __name__=="__main__":
    ara_list_pm().main()

# vim: set et ts=8 sw=4 sts=4:
