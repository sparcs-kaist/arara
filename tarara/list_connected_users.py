#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
import widget
import listview
from ara_form import *

class connected_user_rowitem(widget.FieldRow):
    fields = [
        ('id', 10, 'left'),
        ('nickname',10, 'left'),
        ('ip',16, 'left'),
        ('action',0,'left'),
    ]

class ara_list_connected_users(ara_form):
    def keypress(self, size, key):
        if key.lower() == 'q':
            self.parent.change_page('user_information', {'session_key':self.session_key})
        elif key == 'enter':
            # self.userlist.get_body().get_focus()[0].w.w.widget_list : 현재 활성화된 항목
            username = self.userlist.get_body().get_focus()[0].w.w.widget_list[0].get_text()[0]
            self.parent.change_page('query_user', {'session_key':self.session_key, 'default_user':username})
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u'ARA: List connected users',align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.infotext = urwid.Filler(urwid.Text('(s)imple (d)etailed (q)uit (Enter) query'))

        retvalue, users = self.server.login_manager.get_current_online(self.session_key)
        assert retvalue, users
        userlist = []
        if len(users) > 0:
            for user in users:
                userlist += [{'id':user['username'], 'nickname':user['nickname'], 'ip':user['ip'], 'action':'Sleeping'}]
        else:
            userlist = [{'id':' ','nickname':'', 'ip':' ', 'action':u'No users online.'}]

        header = {'id':'ID', 'nickname':'Nickname','ip':'IP Address', 'action':'Action'}
        self.userlist = listview.get_view(userlist, header, connected_user_rowitem)

        content = [('fixed',1, self.header),('fixed',1,self.infotext), self.userlist]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_list_connectusers().main()

# vim: set et ts=8 sw=4 sts=4:
