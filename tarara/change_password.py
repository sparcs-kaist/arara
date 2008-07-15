#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_forms import *

class ara_changepw(ara_forms):
    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def __initwidgets__(self):
	header = urwid.Filler(urwid.Text("ARA: Change Password", align='center'))

        oldpwedit = urwid.Filler(urwid.Edit(caption="Old password:", wrap='clip'))
        oldpwdesc = urwid.Filler(urwid.Text("Please enter your\nold password"))
        oldpwcolumn = self._make_column(oldpwedit, oldpwdesc)

        newpwedit = urwid.Filler(urwid.Edit(caption="New password:", wrap='clip'))
        newpwdesc = urwid.Filler(urwid.Text("Minimum password length\nis 4 characters"))
        newpwcolumn = self._make_column(newpwedit, newpwdesc)

        confirmedit = urwid.Filler(urwid.Edit(caption="Confirm\nnew password:", wrap='clip'))
        confirmdesc = urwid.Filler(urwid.Text("Re-enter your new\npassword"))
        confirmcolumn = self._make_column(confirmedit, confirmdesc)

        self.joinpile = urwid.Pile([oldpwcolumn, newpwcolumn,confirmcolumn])

        joinbutton = urwid.Filler(urwid.Button("OK"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(joinbutton, cancelbutton, 50, 50)

        langitems = [urwid.Text('Korean'), urwid.Text('English'), urwid.Text('Chinese')]
        self.langlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(langitems)))

        infotext = urwid.Filler(urwid.Text("""  * Press [Enter] to proceed to the next item, [Shift+Enter] - previous item
  * Press [Tab] to directly jump to OK or Cancel button"""))

        content = [('fixed',1,header),self.joinpile,('fixed',2,infotext),('fixed',1,self.blank),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

        return self.mainpile

if __name__=="__main__":
    ara_changepw().main()

# vim: set et ts=8 sw=4 sts=4:
