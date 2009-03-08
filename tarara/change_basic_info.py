#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
from translation import _

class ara_change_basic_info(ara_form):
    def keypress(self, size, key):
        self.mainpile.keypress(size, key)
        
    def on_button_clicked(self, button):
        retvalue = None
        if button == self.okbutton.body:
            if self.server.member_manager.is_registered_nickname(self.nickedit.body.get_edit_text()):
                confirm = widget.Dialog(_('Nickname is in use.\nTry another one.'), [_('OK')], ('menu', 'bg', 'bgf'), 30, 6, self)
                self.overlay = confirm
                self.parent.run()
                if confirm.b_pressed == _('OK'):
                    self.parent.change_page("change_basic_info",{'session_key':self.session_key})
                else:
                    pass
                return
            else:
                self.myinfo['nickname'] = self.nickedit.body.get_edit_text()
                try:
                    self.server.member_manager.modify(self.session_key, self.myinfo)
                    message = _('Nickname changed.')
                except InvalidOperation, e:
                    message = e.why
                except InternalError, e:
                    message = e.why
                confirm = widget.Dialog(message, [_('OK')], ('menu', 'bg', 'bgf'), 30, 6, self)
                self.overlay = confirm
                self.parent.run()
                if confirm.b_pressed == _('OK'):
                    self.parent.change_page("user_preferences",{'session_key':self.session_key})
                else:
                    pass
                return
        elif button == self.cancelbutton.body:
            self.parent.change_page("user_preferences", {'session_key':self.session_key})

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(_('ARA: Change Basic Information'), align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.myinfo = self.server.member_manager.get_info(self.session_key)

        idtext = urwid.Filler(urwid.Text(_('ID: %s') % self.myinfo['username']))
        iddesc = urwid.Filler(urwid.Text(_('ID and E-Mail couldn\'t be edited\nDisplayed for your information')))
        idcolumn = widget.EasyColumn(idtext, iddesc)

        emailtext = urwid.Filler(urwid.Text(_('E-Mail: %s') % self.myinfo['email']))
        emailcolumn = widget.EasyColumn(emailtext, widget.blanktext)

        self.nickedit = urwid.Filler(urwid.Edit(caption=_('Nickname: '), wrap='clip'))
        self.nickedit.body.set_edit_text(self.myinfo['nickname'])
        nickdesc = urwid.Filler(urwid.Text(_('You can\'t use duplicated\nnickname or other\'s ID')))
        nickcolumn = widget.EasyColumn(self.nickedit, nickdesc)

	langtext = urwid.Filler(urwid.Text(_('Language:')))
        langitems = ['Korean', 'English','Chinese']
        langitems = [widget.Item(text, None, 'selected') for text in langitems]
        self.langlist = widget.Border(urwid.ListBox(urwid.SimpleListWalker(langitems)))
	self.lang = urwid.Columns([langtext, self.langlist])
        langdesc = urwid.Filler(urwid.Text(_('Select your favorite\ninterface language')))
	langcolumn = widget.EasyColumn(self.lang, langdesc)

        self.contentpile = urwid.Pile([('fixed',2,idcolumn), ('fixed',2,emailcolumn), ('fixed',2,nickcolumn), langcolumn])

        self.okbutton = urwid.Filler(urwid.Button(_('OK'), self.on_button_clicked))
        self.cancelbutton = urwid.Filler(urwid.Button(_('Cancel'), self.on_button_clicked))
        buttoncolumn = widget.EasyColumn(self.okbutton, self.cancelbutton, 50, 50)

        infotext = urwid.Filler(urwid.Text(_("""  * Press [Enter] to proceed to the next item, [Shift+Enter] - previous item
  * Press [Tab] to directly jump to OK or Cancel button""")))

        content = [('fixed',1,self.header),('fixed',1,widget.blanktext),self.contentpile,('fixed',2,infotext),('fixed',1,widget.blank),('fixed',1,buttoncolumn)]
        self.mainpile = urwid.Pile(content)

# vim: set et ts=8 sw=4 sts=4:
