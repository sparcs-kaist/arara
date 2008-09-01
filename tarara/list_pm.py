#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
import listview
from translation import _

class pmlist_rowitem(widget.FieldRow):
    fields = [
        ('number', 4, 'left'),
        ('new', 1, 'right'),
        ('author',12, 'left'),
        ('title',0, 'left'),
        ('date',5, 'left'),
    ]

class ara_list_pm(ara_form):
    def display_inbox(self):
        self.list_header = {'new':'N', 'number':'#', 'author':_('Author'), 'title':_('Title'), 'date':_('Date')}
        self.pmlist.set_header(listview.make_header(self.list_header, pmlist_rowitem))

        # Acqure messages
        ret, receive_list = self.server.messaging_manager.receive_list(self.session_key, 1, 10)
        assert ret, receive_list
        message_list = receive_list['hit']

        # Generate message_item
        message_item = []
        if len(message_list) < 1:
            # If no message...
            self.hasmessage = False
            message_item = [{'new':'', 'number':'', 'author':'','title':_('No private messages. Have a nice day.'),'date':''}]
        else:
            # Otherwise...
            self.hasmessage = True
            for msg in message_list:
                message_item += [{'new':str(msg['read_status']), 'number':str(msg['id']), 'author':msg['from'], 'title':msg['message'], 'date':msg['sent_time'].strftime("%m/%d")}]
        self.pmlist.set_body(listview.make_body(message_item, pmlist_rowitem))

    def display_outbox(self):
        self.list_header = {'new':'N', 'number':'#', 'author':_('Recepient'), 'title':_('Title'), 'date':_('Date')}
        self.pmlist.set_header(listview.make_header(self.list_header, pmlist_rowitem))

        # Acquire messages
        ret, sent_list = self.server.messaging_manager.sent_list(self.session_key, 1, 10)
        assert ret, sent_list
        message_list = sent_list['hit']
        
        # Generate message_item
        message_item = []
        if len(message_list) < 1:
            # If no message...
            self.hasmessage = False
            message_item = [{'new':'', 'number':'', 'author':'','title':_('No private messages. Have a nice day.'),'date':''}]
        else:
            # Otherwise...
            self.hasmessage = True
            for msg in message_list:
                message_item += [{'new':str(msg['read_status']), 'number':str(msg['id']), 'author':msg['to'], 'title':msg['message'], 'date':msg['sent_time'].strftime("%m/%d")}]
        self.pmlist.set_body(listview.make_body(message_item, pmlist_rowitem))

    def keypress(self, size, key):
        if key in self.keymap:
            key = self.keymap[key]
        mainpile_focus = self.mainpile.get_focus()
        if key == 'w':
            self.parent.change_page("write_pm", {'session_key':self.session_key, 'mode':'write', 'reply_to' : ''})
        elif key == 'r':
            self.parent.change_page("write_pm", {'session_key':self.session_key, 'mode':'reply', 'reply_to' : 'me'})
        elif key == 'q':
            self.parent.change_page("main", {'session_key':self.session_key})
        elif mainpile_focus == self.pmlist and key=='enter':
            if self.hasmessage:
                pm_id = int(self.pmlist.get_body().get_focus()[0].w.w.widget_list[0].get_text()[0])
        else:
            self.mainpile.keypress(size, key)

    def on_button_pressed(self, button):
        if button == self.inboxbutton.body:
            self.display_inbox()
        elif button == self.outboxbutton.body:
            self.display_outbox()

    def __initwidgets__(self):
        self.keymap = {
            'j':'down',
            'k':'up',
            'N':'page down',
            'P':'page up',
        }
	self.header = urwid.Filler(urwid.Text(_('ARA: Private message'),align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.infotext = urwid.Filler(urwid.Text(_(' (N)ext/(P)revious Page (w)rite (B)lock (h)elp (q)uit')))

        itemlist = [{'new':'N', 'number':'1', 'author':'dummy','title':'item','date':'1/1'}]
        self.list_header = {'new':'N', 'number':'#', 'author':_('Author'), 'title':_('Title'), 'date':_('Date')}

        self.pmlist = listview.get_view(itemlist, self.list_header, pmlist_rowitem)

        self.inboxbutton = urwid.Filler(urwid.Button(_('Inbox'), self.on_button_pressed))
        self.outboxbutton = urwid.Filler(urwid.Button(_('Outbox'), self.on_button_pressed))
        self.buttoncolumn = widget.EasyColumn(self.inboxbutton, self.outboxbutton, 50, 50)

        content = [('fixed',1, self.header),('fixed',1,self.infotext),('fixed',1,self.buttoncolumn),self.pmlist,]
        self.mainpile = urwid.Pile(content)

        self.display_inbox()

# vim: set et ts=8 sw=4 sts=4:
