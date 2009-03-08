#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
import listview
from translation import _
from article_list_walker import ArticleListWalker
from article_search_walker import ArticleSearchWalker

class articlelist_rowitem(widget.FieldRow):
    fields = [
        ('number', 4, 'left'),
        ('new', 1, 'right'),
        ('author',12, 'left'),
        ('title',0, 'left'),
        ('date',5, 'left'),
        ('hit',7, 'left'),
        ('vote',4, 'left'),
    ]

class articlelist_rowitem_guest(widget.FieldRow):
    fields = [
        ('number', 4, 'left'),
        ('author',12, 'left'),
        ('title',0, 'left'),
        ('date',5, 'left'),
        ('hit',7, 'left'),
        ('vote',4, 'left'),
    ]

class ara_list_article(ara_form):
    def __init__(self, parent, session_key = None, board_name = None):
        self.board_name = board_name
        ara_form.__init__(self, parent, session_key)

    def make_widget(self, data):
        w = articlelist_rowitem(data)
        return widget.MarkedItem('>', w)

    def make_widget_guest(self, data):
        w = articlelist_rowitem_guest(data)
        return widget.MarkedItem('>', w)

    def keypress(self, size, key):
        if key in self.keymap:
            key = self.keymap[key]
        if key == "enter" and not self.session_key == 'guest':
            # self.boardlist.get_body().get_focus()[0].w.w.widget_list : 현재 활성화된 항목
            article_id = self.articlelist.get_body().get_focus()[0].w.w.widget_list[0].get_text()[0]
            if article_id != '':
                article_id = int(article_id)
                self.parent.change_page("read_article", {'session_key':self.session_key, 'board_name':self.board_name, 'article_id':article_id})
        elif key == 'w' and not self.readonly and not self.session_key == 'guest':
            self.parent.change_page('post_article', {'session_key':self.session_key, 'board_name':self.board_name, 'mode':'post', 'article_id':''})
        elif key == 'q':
            self.parent.change_page("main", {'session_key':self.session_key})
        elif key == 'f':
            if self.session_key == 'guest':
                return
            input_dialog = widget.Dialog(_('Search term:'), [_('OK'), _('Cancel')], ('menu','bg','bgf'), 30, 7, self, 'Text')
            self.overlay = input_dialog
            self.parent.run()
            if input_dialog.b_pressed == _('OK'):
                search_term = input_dialog.edit_text
            else:
                search_term = ''
            if search_term.strip() == '':
                return
            listbody = urwid.ListBox(ArticleSearchWalker(self.session_key, self.board_name,
                self.make_widget, False, {'title':search_term}))
            self.articlelist.set_body(listbody)
            self.overlay = None
            self.parent.run()
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
        self.keymap = {
            'n': 'down',
            'j': 'down',
            'p': 'up',
            'k': 'up',
            'N': 'page down',
            'P': 'page up',
            ' ': 'enter',
            'ctrl p': 'w',
        }

        boardinfo = self.server.board_manager.get_board(self.board_name)
        self.readonly = boardinfo.read_only

	self.header = urwid.Filler(urwid.Text(_('ARA: Article list'),align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.infotext1 = urwid.Filler(urwid.Text(_('(N)ext/(P)revious Page (Number+Enter) Jump to article')))
        if self.session_key == 'guest':
            self.infotext2 = urwid.Filler(urwid.Text(_('(h)elp (q)uit')))
        else:
            if self.readonly:
                self.infotext2 = urwid.Filler(urwid.Text(_('(Enter,space) Read (f)ind (h)elp (q)uit')))
            else:
                self.infotext2 = urwid.Filler(urwid.Text(_('(Enter,space) Read (w)rite (f)ind (h)elp (q)uit')))
        
        # ArticleListWalker
        # TODO: 검색 시 ArticleSearchWalker를 사용하도록 변경.
        if self.session_key == 'guest':
            body = urwid.ListBox(ArticleListWalker(self.session_key, self.board_name, self.make_widget_guest))
            header = {'number':'#', 'author':_('Author'), 'title':_('Title'), 'date':_('Date'), 'hit':_('Hit'), 'vote':_('Vote')}
            header = listview.make_header(header, articlelist_rowitem_guest)
        else:
            body = urwid.ListBox(ArticleListWalker(self.session_key, self.board_name, self.make_widget))
            header = {'new':'N', 'number':'#', 'author':_('Author'), 'title':_('Title'), 'date':_('Date'), 'hit':_('Hit'), 'vote':_('Vote')}
            header = listview.make_header(header, articlelist_rowitem)
        self.articlelist = urwid.Frame(body, header)

        content = [('fixed',1, self.header),('fixed',1,self.infotext1),('fixed',1,self.infotext2),self.articlelist,]
        self.mainpile = urwid.Pile(content)

# vim: set et ts=8 sw=4 sts=4:
