#!/usr/bin/python
# coding: utf-8

import sys
import urwid.curses_display
import urwid
from ara_form import *
import widget
from helpviewer import *
from translation import _

class ara_main(ara_form):
    menu = [
        _('(N)ew Article'),
        _('(S)elect Board'),
        _('(P)rivate Message'),
        _('(U)ser Preferences'),
        _('User (I)nformation'),
        _('(H)elp'),
        _('(A)bout ARA'),
        _('(W)elcome Screen'),
        _('(Q)uit'),
    ]

    def show_help(self):
        confirm = HelpDialog('ara_help', ('menu','bg','bgf'), 40, 15, self)
        self.overlay = confirm
        self.parent.run()
        if confirm.quit:
            self.overlay = None
            self.parent.run()

    def show_about(self):
        confirm = HelpDialog('about', ('menu','bg','bgf'), 40, 15, self)
        self.overlay = confirm
        self.parent.run()
        if confirm.quit:
            self.overlay = None
            self.parent.run()

    def notify_guest(self):
        confirm = widget.Dialog(_('Not available in guest mode.'), [_('Ok')], ('menu', 'bg', 'bgf'), 35, 5, self)
        self.overlay = confirm
        self.parent.run()
        self.overlay = None
        self.parent.run()

    def confirm_quit(self):
        confirm = widget.Dialog(_('Really quit?'), [_('Yes'), _('No')], ('menu', 'bg', 'bgf'), 30, 5, self)
        self.overlay = confirm
        self.parent.run()
        if confirm.b_pressed == _('Yes'):
            self.server.login_manager.logout(self.session_key)
            sys.exit(0)
        else:
            self.overlay = None
            self.parent.run()

    def keypress(self, size, key):
        if key in self.keymap:
            key = self.keymap[key]
        if "tab" in key:
            if self.maincolumn.get_focus() == self.menulist:
                self.maincolumn.set_focus(self.bests)
            elif self.maincolumn.get_focus() == self.bests:
                self.maincolumn.set_focus(self.menulist)
        elif key.lower() == 'n':
            self.menulist.set_focus(0)
        elif key.lower() == 's':
            self.menulist.set_focus(1)
            self.parent.change_page("list_boards", {'session_key':self.session_key})
        elif key.lower() == 'p':
            if self.session_key == 'guest':
                self.notify_guest()
            else:
                self.menulist.set_focus(2)
                self.parent.change_page("list_pm", {'session_key':self.session_key})
        elif key.lower() == 'u':
            if self.session_key == 'guest':
                self.notify_guest()
            else:
                self.menulist.set_focus(3)
                self.parent.change_page("user_preferences", {'session_key':self.session_key})
        elif key.lower() == 'i':
            if self.session_key == 'guest':
                self.notify_guest()
            else:
                self.menulist.set_focus(4)
                self.parent.change_page("user_information", {'session_key':self.session_key})
        elif key.lower() == 'h':
            self.menulist.set_focus(5)
            self.show_help()
        elif key.lower() == 'a':
            self.menulist.set_focus(6)
            self.show_about()
        elif key.lower() == 'w':
            self.menulist.set_focus(7)
            self.parent.change_page("welcome", {'session_key':self.session_key})
        elif key.lower() == 'q':
            self.menulist.set_focus(8)
            self.confirm_quit()
        elif key == "enter":
            maincolumn_focus = self.maincolumn.get_focus()
            if maincolumn_focus == self.menulist:
                pos = self.menulist.get_focus()[1]
                if pos == 0:
                    # TODO: 새 글 읽기로 가기
                    pass
                elif pos == 1:
                    self.parent.change_page("list_boards", {'session_key':self.session_key})
                elif pos == 2:
                    if self.session_key == 'guest':
                        self.notify_guest()
                    else:
                        self.parent.change_page("list_pm", {'session_key':self.session_key})
                elif pos == 3:
                    if self.session_key == 'guest':
                        self.notify_guest()
                    else:
                        self.parent.change_page("user_preferences", {'session_key':self.session_key})
                elif pos == 4:
                    if self.session_key == 'guest':
                        self.notify_guest()
                    else:
                        self.parent.change_page("user_information", {'session_key':self.session_key})
                elif pos == 5:
                    self.show_help()
                elif pos == 6:
                    self.show_about()
                elif pos == 7:
                    self.parent.change_page("welcome", {'session_key':self.session_key})
                elif pos == 8:
                    self.confirm_quit()
            elif maincolumn_focus == self.bests:
                if self.session_key == 'guest':
                    self.notify_guest()
                else:
                    bests_focus = self.bests.get_focus()
                    if bests_focus == self.todaybest:
                        selected = self.tblist_raw[self.tblist.get_focus()[1]]
                        self.parent.change_page("read_article", {'session_key':self.session_key,
                            'board_name':selected['board_name'], 'article_id':selected['id']})
                    elif bests_focus == self.weeklybest:
                        selected = self.wblist_raw[self.wblist.get_focus()[1]]
                        self.parent.change_page("read_article", {'session_key':self.session_key,
                            'board_name':selected['board_name'], 'article_id':selected['id']})
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
        self.keymap = {
            'j':'down',
            'k':'up',
        }
	self.header = urwid.Filler(urwid.Text(_('ARA: Main Menu'), align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        menuitems = [widget.Item(" * "+w+"\n", None, 'selected') for w in self.menu]
        self.menulist = urwid.ListBox(urwid.SimpleListWalker(menuitems))

	tbtext = urwid.Filler(urwid.Text(_('Today Best'), align='center'))
        retvalue, self.tblist_raw = self.server.article_manager.get_today_best_list()
        assert retvalue
        tbitems = ["%(title)s (%(nickname)s, %(date)s)" % {"title":text['title'],
            'nickname':text['author_nickname'],'date':text['date'].strftime("%Y/%m/%d")} for text in self.tblist_raw]
        tbitems = [widget.Item(w, None, 'selected') for w in tbitems]
        self.tblist = urwid.ListBox(urwid.SimpleListWalker(tbitems))
	self.todaybest = urwid.Pile([('fixed',1,tbtext), self.tblist])

	wbtext = urwid.Filler(urwid.Text(_('Weekly Best'), align='center'))
        retvalue, self.wblist_raw = self.server.article_manager.get_weekly_best_list()
        assert retvalue
        wbitems = ["%(title)s (%(nickname)s, %(date)s)" % {"title":text['title'],
            'nickname':text['author_nickname'],'date':text['date'].strftime("%Y/%m/%d")} for text in self.wblist_raw]
        wbitems = [widget.Item(w, None, 'selected') for w in wbitems]
        self.wblist = urwid.ListBox(urwid.SimpleListWalker(wbitems))
	self.weeklybest = urwid.Pile([('fixed',1,wbtext), self.wblist])

	self.bests = urwid.Pile([self.todaybest, self.weeklybest])
	self.copyrightnotice = urwid.Filler(urwid.Text(
_("""  * Press [Tab] to jump between menu, today best, weekly best
 ARAra Release 1.0                                Copyright (C) 2008, SPARCS""")))

        self.maincolumn = urwid.Columns([('weight',40,self.menulist),('weight',60,self.bests)])

        content = [('fixed',1, self.header),('fixed',1,widget.blanktext),
                self.maincolumn, ('fixed',1,widget.dash),
                ('fixed',2,self.copyrightnotice)]
        self.mainpile = urwid.Pile(content)

        self.keymap = {
            "left":"",
            "right":"",
            "j":"down",
            "k":"up",
            }

# vim: set et ts=8 sw=4 sts=4:
