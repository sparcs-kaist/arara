#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_change_password(ara_form):
    def keypress(self, size, key):
        self.mainpile.keypress(size, key)
        
    def on_button_clicked(self, button):
        if button == self.okbutton.body:
            if self.newpwedit.body.get_edit_text() == self.confirmedit.body.get_edit_text():
                print self.server.member_manager.modify_password(self.session_key, {
                    'username':self.server.member_manager.get_info(self.session_key)[1]['username'],
                    'current_password':self.oldpwedit.body.get_edit_text(),
                    'new_password':self.newpwedit.body.get_edit_text()})
        elif button == self.cancelbutton.body:
            self.parent.change_page("user_preferences", {'session_key':self.session_key})

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text("ARA: Change Password", align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')

        self.oldpwedit = urwid.Filler(widget.PasswordEdit(caption="Old password:", wrap='clip'))
        oldpwdesc = urwid.Filler(urwid.Text("Please enter your\nold password"))
        oldpwcolumn = widget.EasyColumn(self.oldpwedit, oldpwdesc)

        self.newpwedit = urwid.Filler(widget.PasswordEdit(caption="New password:", wrap='clip'))
        newpwdesc = urwid.Filler(urwid.Text("Minimum password length\nis 4 characters"))
        newpwcolumn = widget.EasyColumn(self.newpwedit, newpwdesc)

        self.confirmedit = urwid.Filler(widget.PasswordEdit(caption="Confirm\nnew password:", wrap='clip'))
        confirmdesc = urwid.Filler(urwid.Text("Re-enter your new\npassword"))
        confirmcolumn = widget.EasyColumn(self.confirmedit, confirmdesc)

        self.pwpile = urwid.Pile([oldpwcolumn, newpwcolumn,confirmcolumn])

        self.okbutton = urwid.Filler(urwid.Button("OK", self.on_button_clicked))
        self.cancelbutton = urwid.Filler(urwid.Button("Cancel", self.on_button_clicked))
        buttoncolumn = widget.EasyColumn(self.okbutton, self.cancelbutton, 50, 50)

        infotext = urwid.Filler(urwid.Text("""  * Press [Enter] to proceed to the next item, [Shift+Enter] - previous item
  * Press [Tab] to directly jump to OK or Cancel button"""))

        content = [('fixed',1,self.header),self.pwpile,('fixed',2,infotext),('fixed',1,widget.blank),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_changepw().main()

# vim: set et ts=8 sw=4 sts=4:
