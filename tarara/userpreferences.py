#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid

class ara_userpreferences(object):
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
        actionitems = [urwid.Text(text) for text in actions]
        self.actionlist = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(actionitems)))
	actioncolumn = self._make_column(self.actionlist, blanktext)

        self.joinpile = urwid.Pile([idcolumn, nickcolumn,langcolumn,('fixed',1,actiontext),actioncolumn])

        okbutton = urwid.Filler(urwid.Button("OK"))
        cancelbutton = urwid.Filler(urwid.Button("Cancel"))
        buttoncolumn = self._make_column(okbutton, cancelbutton, 50, 50)

        infotext = urwid.Filler(urwid.Text("  * Use [Tab] or arrow key to move each items"))

        content = [('fixed',1,header),self.joinpile,('fixed',1,infotext),('fixed',1,blank),('fixed',1,buttoncolumn)]
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

ara_userpreferences().main()

# vim: set et ts=8 sw=4 sts=4
