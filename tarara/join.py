#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
import re
from common import *

class ara_join(ara_forms):
    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def __keypress__(self, size, key):
        curfocus = self.joinpile.get_focus()
        if key.strip() == 'enter':
            if curfocus == self.idcolumn:
                if self.server.member_manager.is_registered(self.idedit.body.get_edit_text()):
                    self.idedit.body.set_edit_text('')
                else:
                    self.joinpile.set_focus(self.nickcolumn)
            elif curfocus == self.nickcolumn:
                # TODO: 닉네임 중복 확인
                self.joinpile.set_focus(self.pwcolumn)
            elif curfocus == self.pwcolumn:
                self.joinpile.set_focus(self.confirmcolumn)
            elif curfocus == self.confirmcolumn:
                if self.pwedit.body.get_edit_text() != self.confirmedit.body.get_edit_text():
                    self.pwedit.body.set_edit_text('')
                    self.confirmedit.body.set_edit_text('')
                    self.joinpile.set_focus(self.pwcolumn)
                else:
                    self.joinpile.set_focus(self.emailcolumn)
            elif curfocus == self.emailcolumn:
                # TODO: 이메일 중복 확인
                if re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,6}$", self.emailedit.body.get_edit_text()):
                    self.joinpile.set_focus(self.langcolumn)
                else:
                    self.emailedit.body.set_edit_text('')
            elif curfocus == self.langcolumn:
                self.mainpile.set_focus(self.buttoncolumn)
            else:
                pass
        elif key.strip() in ('up','down'):
            if curfocus == self.langcolumn:
                self.frame.keypress(size, key)
        else:
            self.frame.keypress(size, key)

    def on_button_clicked(self, button):
        if button == self.joinbutton:
            reg_dic = {'id':self.idedit.body.get_edit_text(), 'password':self.pwedit.body.get_edit_text(), 'nickname':self.nickedit.body.get_edit_text(), 'email':self.emailedit.body.get_edit_text(), 'sig':'', 'self_introduce':'','default_language':'ko'}
            print self.server.member_manager.register(reg_dic)
        elif button == self.cancelbutton:
            pass

    def __initwidgets__(self):
	header = urwid.Filler(urwid.Text("ARA: Join", align='center'))

        self.idedit = urwid.Filler(urwid.Edit(caption="ID:", wrap='clip'))
        iddesc = urwid.Filler(urwid.Text("ID's length should be\nbetween 4 and 10 chars"))
        self.idcolumn = self._make_column(self.idedit, iddesc)

        self.nickedit = urwid.Filler(urwid.Edit(caption="Nickname:", wrap='clip'))
        nickdesc=urwid.Filler(urwid.Text("You can't use duplicated\nnickname or other's ID"))
        self.nickcolumn = self._make_column(self.nickedit, nickdesc)
        
        self.pwedit = urwid.Filler(urwid.Edit(caption="Password:", wrap='clip'))
        pwdesc = urwid.Filler(urwid.Text("Minimum password length\nis 4 characters"))
        self.pwcolumn = self._make_column(self.pwedit, pwdesc)

        self.confirmedit = urwid.Filler(urwid.Edit(caption="Confirm\nPassword:", wrap='clip'))
        confirmdesc = urwid.Filler(urwid.Text("Type password here\nonce again"))
        self.confirmcolumn = self._make_column(self.confirmedit, confirmdesc)

        self.emailedit = urwid.Filler(urwid.Edit(caption="E-Mail:", wrap='clip'))
        emaildesc = urwid.Filler(urwid.Text("We'll send confirmation\nmail to this address"))
        self.emailcolumn = self._make_column(self.emailedit, emaildesc)

	langtext = urwid.Filler(urwid.Text("Language:"))
        langitems = ['Korean','English','Chinese']
        langitems = [Item(w,None,'selected') for w in langitems]
        self.langlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(langitems)))
	self.lang = urwid.Columns([langtext, self.langlist])
        langdesc = urwid.Filler(urwid.Text("Select your favorite\ninterface language"))
	self.langcolumn = self._make_column(self.lang, langdesc)

        self.joinpile = urwid.Pile([('fixed',2,self.idcolumn), ('fixed',2,self.nickcolumn),('fixed',2,self.pwcolumn),('fixed',3,self.confirmcolumn),('fixed',2,self.emailcolumn),self.langcolumn])

        self.joinbutton = urwid.Filler(urwid.Button("Join", self.on_button_clicked))
        self.cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        self.buttoncolumn = self._make_column(self.joinbutton, self.cancelbutton, 50, 50)

        infotext = urwid.Filler(urwid.Text("""  * Press [Enter] to proceed to the next item, [Shift+Enter] - previous item
  * Press [Tab] to directly jump to Join or Cancel button
  * We'll send confirmation mail to your address.
  * To activate your ID, click the link on the mail."""))

        content = [('fixed',1,header),self.joinpile,('fixed',4,infotext),('fixed',1,self.blank),('fixed',1,self.buttoncolumn)]
        self.mainpile = urwid.Pile(content)

	return self.mainpile

if __name__=="__main__":
    ara_join().main()

# vim: set et ts=8 sw=4 sts=4:
