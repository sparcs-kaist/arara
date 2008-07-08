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
	header = urwid.Filler(urwid.Text("ARA: Change Password", align='center'))

        oldpwedit = urwid.Filler(urwid.Edit(caption="ID:", wrap='clip'))
        oldpwdesc = urwid.Filler(urwid.Text("Please enter your\nold password"))
        oldpwcolumn = self._make_column(oldpwedit, oldpwdesc)

        newpwedit = urwid.Filler(urwid.Edit(caption="Password:", wrap='clip'))
        newpwdesc = urwid.Filler(urwid.Text("Minimum password length\nis 4 characters"))
        newpwcolumn = self._make_column(newpwedit, newpwdesc)

        confirmedit = urwid.Filler(urwid.Edit(caption="Confirm\nnew password:", wrap='clip'))
        confirmdesc = urwid.Filler(urwid.Text("Re-enter your new\npassword"))
        confirmcolumn = self._make_column(confirmedit, confirmdesc)

        self.joinpile = urwid.Pile([oldpwcolumn, newpwcolumn,confirmcolumn])

        joinbutton = urwid.Filler(urwid.Button("Join"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(joinbutton, cancelbutton, 50, 50)

        langitems = [urwid.Text('Korean'), urwid.Text('English'), urwid.Text('Chinese')]
        self.langlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(langitems)))

        infotext = urwid.Filler(urwid.Text("""  * Press [Enter] to proceed to the next item, [Shift+Enter] - previous item
  * Press [Tab] to directly jump to OK or Cancel button"""))

        content = [('fixed',1,header),self.joinpile,('fixed',2,infotext),('fixed',1,blank),('fixed',1,buttoncolumn)]
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
