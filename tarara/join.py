#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid

class ara_join(object):
    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')

    def _make_column(self,widget1, widget2,ratio1=60, ratio2=40):
        return urwid.Columns([
            ('weight', ratio1, widget1),
            ('weight', ratio2, widget2),
            ])

    def __init__(self):
        utf8decode = urwid.escape.utf8decode
        dash = urwid.SolidFill(utf8decode('─'))
        blank = urwid.SolidFill(u" ")
        blanktext = urwid.Filler(urwid.Text(' '))
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

        self.joinpile = urwid.Pile([idcolumn, nickcolumn,pwcolumn,confirmcolumn,emailcolumn])

        joinbutton = urwid.Filler(urwid.Button("Join"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(joinbutton, cancelbutton, 50, 50)

        langitems = [urwid.Text('Korean'), urwid.Text('English'), urwid.Text('Chinese')]
        self.langlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(langitems)))

        infotext = urwid.Filler(urwid.Text("""  * Press [Enter] to proceed to the next item, [Shift+Enter] - previous item
  * Press [Tab] to directly jump to Join or Cancel button
  * We'll send confirmation mail to your address.
  * To activate your ID, click the link on the mail."""))

        content = [('fixed',1,header),self.joinpile,('fixed',4,infotext),('fixed',1,blank),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

        self.frame = self.mainpile

    def main(self):
        self.ui = urwid.curses_display.Screen()
        self.ui.run_wrapper(self.run)

    def run(self):
        size = self.ui.get_cols_rows()
        quit = False
        while not quit:
            self.draw_screen(size)
            keys = self.ui.get_input()
            for key in keys:
                if key == 'tab':
                    quit = True
                    break
#                if key in keymap:
#                    key = keymap[key]
                self.frame.keypress(size, key)
   
    def draw_screen(self, size):
        canvas = self.frame.render(size, focus=True)
        self.ui.draw_screen(size, canvas)

ara_join().main()

# vim: set et ts=8 sw=4 sts=4
