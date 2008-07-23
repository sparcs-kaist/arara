#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *
from widget import *
from change_password import *
from blacklist import *
from sig_intro import *
from set_encoding import *

class ara_user_preferences(ara_forms):
    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def __keypress__(self, size, key):
        key = key.strip().lower()
        mainpile_focus = self.mainpile.get_focus()
        if key == "tab":
            if mainpile_focus == self.contentpile:
                self.mainpile.set_focus(self.buttoncolumn)
            elif mainpile_focus == self.buttoncolumn:
                self.mainpile.set_focus(self.contentpile)
        elif key == "enter":
            if mainpile_focus == self.contentpile:
                contentpile_focus =self.contentpile.get_focus()
                if contentpile_focus == self.actioncolumn:
                    pos = self.actionlist.w.get_focus().get_focus().get_focus()[1]
                    if pos == 0:
                        ara_changepw(self.session_key).main()
                    elif pos == 1:
                        ara_blacklist(self.session_key).main()
                    elif pos == 2:
                        ara_sig_intro(self.session_key).main()
                    elif pos == 3:
                        # TODO: 잽
                        pass
                    elif pos == 4:
                        ara_set_encoding(self.session_key).main()
        else:
            self.frame.keypress(size, key)

    def __initwidgets__(self):
	header = urwid.Filler(urwid.Text("ARA: User Preferences", align='center'))

	self.idedit = urwid.Filler(urwid.Text("ID: %(id)s\nE-Mail: %(email)s" % {"id":"peremen","email":"ara@peremen.name"}))
	iddesc = urwid.Filler(urwid.Text("You can't change ID\nand E-Mail"))
        self.idcolumn = self._make_column(self.idedit, iddesc)

        self.nickedit = urwid.Filler(urwid.Edit(caption="Nickname:", wrap='clip'))
        nickdesc=urwid.Filler(urwid.Text("You can't use duplicated\nnickname"))
        self.nickcolumn = self._make_column(self.nickedit, nickdesc)
        
	langtext = urwid.Filler(urwid.Text("Language:"))
        langitems = ['Korean', 'English','Chinese']
        langitems = [Item(text, None, 'selected') for text in langitems]
        self.langlist = Border(urwid.ListBox(urwid.SimpleListWalker(langitems)))
	self.lang = urwid.Columns([langtext, self.langlist])
        langdesc = urwid.Filler(urwid.Text("Select your favorite\ninterface language"))
	self.langcolumn = self._make_column(self.lang, langdesc)

	actiontext = urwid.Filler(urwid.Text("Actions"))
	actions = ["Change password","View/edit blacklist","Change Introduction/Signature","Zap board","Set terminal encoding"]
        actionitems = [Item(' * '+text, None, 'selected') for text in actions]
        self.actionlist = Border(urwid.ListBox(urwid.SimpleListWalker(actionitems)))
	self.actioncolumn = self._make_column(self.actionlist, self.blanktext)

        self.contentpile = urwid.Pile([('fixed',2,self.idcolumn), ('fixed',2,self.nickcolumn),self.langcolumn,('fixed',1,actiontext),self.actioncolumn])

        self.okbutton = urwid.Filler(urwid.Button("OK"))
        self.cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        self.buttoncolumn = self._make_column(self.okbutton, self.cancelbutton, 50, 50)

        infotext = urwid.Filler(urwid.Text("  * Use [Tab] or arrow key to move each items"))

        content = [('fixed',1,header),self.contentpile,('fixed',1,self.dash),('fixed',1,infotext),('fixed',1,self.blank),('fixed',1,self.buttoncolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_user_preferences().main()

# vim: set et ts=8 sw=4 sts=4:
