#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
import listview

class blacklist_rowitem(widget.FieldRow):
    fields = [
        ('id',3,'left'),
        ('username', 10, 'left'),
        ('nickname',0, 'left'),
        ('block_article',15, 'left'),
        ('block_pm',15,'left'),
    ]

class ara_blacklist(ara_form):
    def keypress(self, size, key):
        self.mainpile.keypress(size, key)

    def on_button_clicked(self, button):
        if button == self.cancelbutton.body:
            self.parent.change_page("user_preferences", {'session_key':self.session_key})

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: My Blacklist",align='center'))
        self.header = urwid.AttrWrap(self.header,'reversed')

        retvalue, self.blacklist = self.server.blacklist_manager.list(self.session_key)
        assert retvalue, self.blacklist
        userlist = []
        if len(self.blacklist) > 0:
            for user in self.blacklist:
                userlist += [{'id':str(user['id']), 'username':user['blacklisted_user_username'], 'nickname':'Nickname',
                    'block_article':'Yes' if user['block_article'] else 'No',
                    'block_pm':'Yes' if user['block_message'] else 'No',
                    }]
        else:
            userlist = [{'id':' ', 'username':' ', 'nickname':'No users blacklisted.',
                'block_article':' ','block_pm':' '}]

        header = {'id':'#', 'username':'ID', 'nickname':'Nickname','block_article':'Block Article','block_pm':'Block Message'}
        self.blacklist_ = listview.get_view(userlist, header, blacklist_rowitem)

        self.savebutton = urwid.Filler(urwid.Button("Save", self.on_button_clicked))
        self.cancelbutton = urwid.Filler(urwid.Button("Cancel", self.on_button_clicked))
        buttoncolumn = widget.EasyColumn(self.savebutton, self.cancelbutton, 50, 50)

        content = [('fixed',1, self.header),self.blacklist_, ('fixed',1,widget.dash),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_blacklist().main()

# vim: set et ts=8 sw=4 sts=4:
