#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from common import *

class ara_userpreferences(ara_forms):
    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def __initwidgets__(self):
	header = urwid.Filler(urwid.Text("ARA: User Preferences", align='center'))

	idedit = urwid.Filler(urwid.Text("ID: %(id)s\nE-Mail: %(email)s" % {"id":"peremen","email":"ara@peremen.name"}))
	iddesc = urwid.Filler(urwid.Text("You can't change ID\nand E-Mail"))
        idcolumn = self._make_column(idedit, iddesc)

        nickedit = urwid.Filler(urwid.Edit(caption="Nickname:", wrap='clip'))
        nickdesc=urwid.Filler(urwid.Text("You can't use duplicated\nnickname"))
        nickcolumn = self._make_column(nickedit, nickdesc)
        
	langtext = urwid.Filler(urwid.Text("Language:"))
        langitems = [urwid.Text('Korean'), urwid.Text('English'), urwid.Text('Chinese')]
        self.langlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(langitems)))
	self.lang = urwid.Columns([langtext, self.langlist])
        langdesc = urwid.Filler(urwid.Text("Select your favorite\ninterface language"))
	langcolumn = self._make_column(self.lang, langdesc)

	actiontext = urwid.Filler(urwid.Text("Actions"))
	actions = ["Change password","View/edit blacklist","Change Introduction/Signature","Zap board","Set terminal encoding"]
        actionitems = [urwid.Text(' * '+text) for text in actions]
        self.actionlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(actionitems)))
	actioncolumn = self._make_column(self.actionlist, self.blanktext)

        self.joinpile = urwid.Pile([('fixed',2,idcolumn), ('fixed',2,nickcolumn),langcolumn,('fixed',1,actiontext),actioncolumn])

        okbutton = urwid.Filler(urwid.Button("OK"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(okbutton, cancelbutton, 50, 50)

        infotext = urwid.Filler(urwid.Text("  * Use [Tab] or arrow key to move each items"))

        content = [('fixed',1,header),self.joinpile,('fixed',1,self.dash),('fixed',1,infotext),('fixed',1,self.blank),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

ara_userpreferences().main()

# vim: set et ts=8 sw=4 sts=4
