#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
import widget
import listview
from ara_form import *
import timer

class connected_user_rowitem(widget.FieldRow):
    fields = [
        ('id', 10, 'left'),
        ('nickname',10, 'left'),
        ('ip',16, 'left'),
        ('time',14, 'left'),
        ('action',0,'left'),
    ]

class ara_list_connected_users(ara_form):
    def keypress(self, size, key):
        if key in self.keymap:
            key = self.keymap[key]
        if key.lower() == 'q':
            self.timer.cancel()
            self.parent.change_page('user_information', {'session_key':self.session_key})
        elif key.lower() == 'm':
            if self.timer.state:
                self.infotext.body.set_text('(r)efresh (m)onitoring:start (q)uit (Enter) query')
                self.timer.cancel()
            else:
                self.infotext.body.set_text('(r)efresh (m)onitoring:stop (q)uit (Enter) query')
                self.timer.start()
        elif key.lower() == 'r':
            self.refresh_view()
        elif key == 'enter':
            # self.userlist.get_body().get_focus()[0].w.w.widget_list : 현재 활성화된 항목
            username = self.userlist.get_body().get_focus()[0].w.w.widget_list[0].get_text()[0]
            self.timer.cancel()
            self.parent.change_page('query_user', {'session_key':self.session_key, 'default_user':username})
        else:
            self.mainpile.keypress(size, key)

    def refresh_view(self):
        retvalue, users = self.server.login_manager.get_current_online(self.session_key)
        assert retvalue, users
        self.userlistitem = []
        if len(users) > 0:
            for user in users:
                self.userlistitem += [{'id':user['username'], 'nickname':user['nickname'],
                    'ip':user['ip'], 'time':user['logintime'].strftime('%m/%d %H:%M:%S'),
                    'action':user['current_action']}]
        else:
            self.userlistitem = [{'id':' ','nickname':'', 'ip':' ', 'time':' ','action':u'No users online.'}]
        self.userlist.set_body(listview.make_body(self.userlistitem, connected_user_rowitem))

    def __initwidgets__(self):
        self.keymap = {
            'j': 'down',
            'k': 'up',
            'N': 'page down',
            'P': 'page up',
        }
	self.header = urwid.Filler(urwid.Text(u'ARA: List connected users',align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.infotext = urwid.Filler(urwid.Text('(r)efresh (m)onitoring:start (q)uit (Enter) query'))

        self.userlistitem = [{'id':'dummy','nickname':'dummy', 'ip':'0.0.0.0', 'time':'local','action':u'dummy'}]
        self.userlistheader = {'id':'ID', 'nickname':'Nickname','ip':'IP Address', 'time':'Login Time', 'action':'Action'}
        self.userlist = listview.get_view(self.userlistitem, self.userlistheader, connected_user_rowitem)
        self.refresh_view()

        content = [('fixed',1, self.header),('fixed',1,self.infotext), self.userlist]
        self.mainpile = urwid.Pile(content)

        self.timer = timer.Timer(10.0, self.refresh_view)

        return self.mainpile

if __name__=="__main__":
    ara_list_connectusers().main()

# vim: set et ts=8 sw=4 sts=4:
