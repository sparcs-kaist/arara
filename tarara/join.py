#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from common import *

class ara_join(ara_forms):
    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')


    def __initwidgets__(self):
	header = urwid.Filler(urwid.Text("ARA: Join", align='center'))

        idedit = urwid.Filler(urwid.Edit(caption="ID:", wrap='clip'))
        iddesc = urwid.Filler(urwid.Text("ID's length should be\nbetween 4 and 10 chars"))
        idcolumn = self._make_column(idedit, iddesc)

        nickedit = urwid.Filler(urwid.Edit(caption="Nickname:", wrap='clip'))
        nickdesc=urwid.Filler(urwid.Text("You can't use duplicated\nnickname or other's ID"))
        nickcolumn = self._make_column(nickedit, nickdesc)
        
        pwedit = urwid.Filler(urwid.Edit(caption="Password:", wrap='clip'))
        pwdesc = urwid.Filler(urwid.Text("Minimum password length\nis 4 characters"))
        pwcolumn = self._make_column(pwedit, pwdesc)

        confirmedit = urwid.Filler(urwid.Edit(caption="Confirm\nPassword:", wrap='clip'))
        confirmdesc = urwid.Filler(urwid.Text("Type password here\nonce again"))
        confirmcolumn = self._make_column(confirmedit, confirmdesc)

        emailedit = urwid.Filler(urwid.Edit(caption="E-Mail:", wrap='clip'))
        emaildesc = urwid.Filler(urwid.Text("We'll send confirmation\nmail to this address"))
        emailcolumn = self._make_column(emailedit, emaildesc)

	langtext = urwid.Filler(urwid.Text("Language:"))
        langitems = [urwid.Text('Korean'), urwid.Text('English'), urwid.Text('Chinese')]
        self.langlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(langitems)))
	self.lang = urwid.Columns([langtext, self.langlist])
        langdesc = urwid.Filler(urwid.Text("Select your favorite\ninterface language"))
	langcolumn = self._make_column(self.lang, langdesc)

        self.joinpile = urwid.Pile([idcolumn, nickcolumn,pwcolumn,confirmcolumn,langcolumn])

        joinbutton = urwid.Filler(urwid.Button("Join"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(joinbutton, cancelbutton, 50, 50)


        infotext = urwid.Filler(urwid.Text("""  * Press [Enter] to proceed to the next item, [Shift+Enter] - previous item
  * Press [Tab] to directly jump to Join or Cancel button
  * We'll send confirmation mail to your address.
  * To activate your ID, click the link on the mail."""))

        content = [('fixed',1,header),self.joinpile,('fixed',4,infotext),('fixed',1,self.blank),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

	return self.mainpile

ara_join().main()

# vim: set et ts=8 sw=4 sts=4
