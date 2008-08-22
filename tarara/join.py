#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
import re
from ara_form import *
import widget

class ara_join(ara_form):
    def keypress(self, size, key):
        if key == 'enter':
            if self.mainpile.get_focus() == self.joinpile:
                curfocus = self.joinpile.get_focus()
                if curfocus == self.idcolumn:
                    if self.server.member_manager.is_registered(self.idedit.body.get_edit_text()):
                        self.idedit.body.set_edit_text('')
                    else:
                        self.joinpile.set_focus(self.nickcolumn)
                elif curfocus == self.nickcolumn:
                    if self.server.member_manager.is_registered_nickname(self.nickedit.body.get_edit_text()):
                        self.nickedit.body.set_edit_text('')
                    else:
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
                    text = self.emailedit.body.get_edit_text()
                    is_registered = self.server.member_manager.is_registered_email(text)
                    is_valid_form = re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,6}$", text) 
                    if not is_registered and is_valid_form:
                        self.joinpile.set_focus(self.langcolumn)
                    else:
                        self.emailedit.body.set_edit_text('')
                elif curfocus == self.langcolumn:
                    self.mainpile.set_focus(self.buttoncolumn)
                else:
                    self.mainpile.keypress(size, key)
            elif self.mainpile.get_focus() == self.buttoncolumn:
                self.buttoncolumn.keypress(size, key)
        elif key in ('up','down'):
            curfocus = self.joinpile.get_focus()
            if curfocus == self.langcolumn:
                press = False
                curcolumn = self.langlist.w.get_focus().get_focus().get_focus()[1]
                if curcolumn in range(1,2):
                    press = True
                elif curcolumn == 0:
                    if key.strip() == 'down':
                        press = True
                elif curcolumn == 2:
                    if key.strip() == 'up':
                        press = True
                if press:
                    self.mainpile.keypress(size, key)
            else:
                pass
        elif key == 'tab':
            if self.mainpile.get_focus() == self.joinpile:
                self.mainpile.set_focus(self.buttoncolumn)
            elif self.mainpile.get_focus() == self.buttoncolumn:
                self.mainpile.set_focus(self.joinpile)
        else:
            self.mainpile.keypress(size, key)

    def on_button_clicked(self, button):
        retvalue = None
        if button == self.joinbutton.body:
            reg_dic = {'username':self.idedit.body.get_edit_text(), 'password':self.pwedit.body.get_edit_text(),
                'nickname':self.nickedit.body.get_edit_text(), 'email':self.emailedit.body.get_edit_text(),
                'signature':'', 'self_introduction':'','default_language':'ko'}
            retvalue, reg_key = self.server.member_manager.register(reg_dic)
            if retvalue:
                self.server.member_manager.send_mail(self.emailedit.body.get_edit_text(), self.idedit.body.get_edit_text(),
                    reg_key)
                confirm = widget.Dialog("Account created.\nPlease confirm it.", 
                        ["OK"], ('menu', 'bg', 'bgf'), 30, 6, self)
                self.overlay = confirm
                self.parent.run()
                if confirm.b_pressed == "OK":
                    self.parent.change_page("login",{})
            else:
                message = widget.Dialog(reg_key, ["OK"], ('menu', 'bg', 'bgf'), 30, 6, self)
                self.overlay = message
                self.parent.run()
                if message.b_pressed == "OK":
                    self.parent.change_page("login",{})
        elif button == self.cancelbutton.body:
            self.parent.change_page("login",{})

    def __initwidgets__(self):
	header = urwid.Filler(urwid.Text("ARA: Join", align='center'))
	header = urwid.AttrWrap(header, 'reversed')

        self.idedit = urwid.Filler(urwid.Edit(caption="ID:", wrap='clip'))
        iddesc = urwid.Filler(urwid.Text("ID's length should be\nbetween 4 and 10 chars"))
        self.idcolumn = widget.EasyColumn(self.idedit, iddesc)

        self.nickedit = urwid.Filler(urwid.Edit(caption="Nickname:", wrap='clip'))
        nickdesc=urwid.Filler(urwid.Text("You can't use duplicated\nnickname or other's ID"))
        self.nickcolumn = widget.EasyColumn(self.nickedit, nickdesc)
        
        self.pwedit = urwid.Filler(widget.PasswordEdit(caption="Password:", wrap='clip'))
        pwdesc = urwid.Filler(urwid.Text("Minimum password length\nis 4 characters"))
        self.pwcolumn = widget.EasyColumn(self.pwedit, pwdesc)

        self.confirmedit = urwid.Filler(widget.PasswordEdit(caption="Confirm\nPassword:", wrap='clip'))
        confirmdesc = urwid.Filler(urwid.Text("Type password here\nonce again"))
        self.confirmcolumn = widget.EasyColumn(self.confirmedit, confirmdesc)

        self.emailedit = urwid.Filler(urwid.Edit(caption="E-Mail:", wrap='clip'))
        emaildesc = urwid.Filler(urwid.Text("We'll send confirmation\nmail to this address"))
        self.emailcolumn = widget.EasyColumn(self.emailedit, emaildesc)

	langtext = urwid.Filler(urwid.Text("Language:"))
        langitems = ['Korean','English','Chinese']
        langitems = [widget.Item(w,None,'selected') for w in langitems]
        self.langlist = widget.Border(urwid.ListBox(urwid.SimpleListWalker(langitems)))
	self.lang = urwid.Columns([langtext, self.langlist])
        langdesc = urwid.Filler(urwid.Text("Select your favorite\ninterface language"))
	self.langcolumn = widget.EasyColumn(self.lang, langdesc)

        self.joinpile = urwid.Pile([('fixed',2,self.idcolumn), ('fixed',2,self.nickcolumn),('fixed',2,self.pwcolumn),('fixed',3,self.confirmcolumn),('fixed',2,self.emailcolumn),self.langcolumn])

        self.joinbutton = urwid.Filler(urwid.Button("Join", self.on_button_clicked))
        self.cancelbutton = urwid.Filler(urwid.Button("Cancel", self.on_button_clicked))
        self.buttoncolumn = widget.EasyColumn(self.joinbutton, self.cancelbutton, 50, 50)

        infotext = urwid.Filler(urwid.Text("""  * Press [Enter] to proceed to the next item, [Shift+Enter] - previous item.
  * Press [Tab] to directly jump to Join or Cancel button.
  * Please be patient after click Join button. We'll send confirmation mail.
  * After join, you should activate your ID via link on the mail."""))

        content = [('fixed',1,header),self.joinpile,('fixed',4,infotext),('fixed',1,widget.blank),('fixed',1,self.buttoncolumn)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_join().main()

# vim: set et ts=8 sw=4 sts=4:
