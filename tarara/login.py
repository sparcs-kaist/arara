#!/usr/bin/python
# coding: utf-8

import os
import socket
import urwid.curses_display
import urwid
from ara_form import *
import widget

import gettext
LOCALE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
t = gettext.translation('ara', LOCALE_PATH)
_ = t.ugettext

class ara_login(ara_form):
    def get_remote_ip(self):
        try:
            ip = socket.gethostbyname(os.environ['REMOTEHOST'])
        except KeyError:
            ip = '127.0.0.1'
        return ip

    def get_login_message(self):
        basedir = os.path.dirname(__file__)
        banner = os.path.join(basedir, 'login.txt')
        f = open(banner, 'r')
        return f.read().decode('utf-8')
    
    def login(self, id, password, ip):
        retvalue = None
        try:
            retvalue, message = self.server.login_manager.login(id, password, ip)
        except:
            retvalue, message = [False, 'SERVER_ERROR']
        if retvalue == True:
            pass
        else:
            if message  == 'WRONG_USERNAME':
                self.errormessage.body.set_text(_("Specified ID doesn't exist."))
            elif message == 'WRONG_PASSWORD':
                self.errormessage.body.set_text(_("Wrong password."))
            elif message == 'DATABASE_ERROR':
                self.errormessage.body.set_text(_("Database error."))
            elif message == 'SERVER_ERROR':
                self.errormessage.body.set_text(_("XML-RPC server problem. Try again after several minutes."))
            else:
                self.errormessage.body.set_text(_("Undefined error."))
                assert("Undefined error")
            self.idedit.body.set_edit_text("")
            self.pwedit.body.set_edit_text("")
            self.idpwpile.set_focus(0)
        return retvalue, message

    def keypress(self, size, key):
        curfocus = self.bottomcolumn.get_focus_column()
        if key.strip() == 'tab':
            self.bottomcolumn.set_focus_column((curfocus + 1) % 3)
        elif key.strip() == 'enter':
            if curfocus == 0:
                curpos = self.idpwpile.get_focus()
                if (curpos == self.idedit) & (self.idedit.body.get_edit_text().strip() != ""):
                    self.idpwpile.set_focus(1)
                elif (curpos == self.pwedit) & (self.pwedit.body.get_edit_text().strip() != ""):
                    retvalue, session_key = self.login(self.idedit.body.get_edit_text(), self.pwedit.body.get_edit_text(), self.get_remote_ip())
                    if retvalue:
                        self.parent.change_page("welcome", {'session_key':session_key})
            elif curfocus == 1:
                langindex = self.langlist.w.get_focus().get_focus().get_focus()[1]
            elif curfocus == 2:
                row = self.joinlist.w.get_focus().get_focus().get_focus()[1]
                if row ==0:
                    self.parent.change_page("join", {})
                elif row == 1:
                    session_key = 'guest'
                    self.parent.change_page("welcome", {'session_key':session_key})
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
        self.message = urwid.Filler(urwid.Text(self.get_login_message(), align="center"))
        self.errormessage = urwid.Filler(urwid.Text("", align="center"))
        self.message_ko = urwid.Filler(urwid.Text(u"[Tab] 키를 누르면 항목간을 전환할 수 있습니다", align='center'))
        self.message_en = urwid.Filler(urwid.Text(u"Press [Tab] key to jump between each items", align='center'))
        retvalue, count = self.server.login_manager.total_visitor()
        self.counter = urwid.Filler(urwid.Text(u"Today: %s Total: %s" %
            (count['today_visitor_count'], count['total_visitor_count']), align='center'))

        self.idedit = urwid.Filler(urwid.Edit(caption="ID: ", wrap='clip'))
        self.pwedit = urwid.Filler(widget.PasswordEdit(caption="Password: ", wrap='clip'))
        self.idpwpile = urwid.Pile([self.idedit, self.pwedit])

        langitems = ['Korean','English','Chinese']
        langitems = [widget.Item(w, None, 'selected') for w in langitems]
        self.langlist = widget.Border(urwid.ListBox(urwid.SimpleListWalker(langitems)))

        joinitems = ['Join','Guest']
        joinitems = [widget.Item(w, None, 'selected') for w in joinitems]
        self.joinlist = widget.Border(urwid.ListBox(urwid.SimpleListWalker(joinitems)))

        self.bottomcolumn = urwid.Columns([('weight',40,self.idpwpile),('weight',30,self.langlist),('weight',30,self.joinlist)])

        content = [self.message,('fixed',1,self.errormessage),('fixed',1, widget.dash),
                ("fixed",1,self.counter), ("fixed", 1, self.message_ko),
                ('fixed',1,self.message_en), ('fixed',5,self.bottomcolumn)]
        self.mainpile = urwid.Pile(content)

        self.keymap = {'left':'', 'right':''}

if __name__ == "__main__":
    ara_login().main()

# vim: set et ts=8 sw=4 sts=4:
