#!/usr/bin/python
import urwid
import xmlrpclib
from configuration import *
from translation import _
import os, sys
from datetime import date

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gen-py"))
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(THRIFT_PATH)
sys.path.append(PROJECT_PATH)

import arara
from arara_thrift.ttypes import *

class ArticleListWalker(urwid.ListWalker):
    def __init__(self, session_key, board_name, callback):
        self.server = arara.get_server()
        self.session_key = session_key
        self.board_name = board_name
        self.callback = callback
        self.fetch_size = 30
        self.cached_page = []

        self.fetched_page = [1,]
        self.fetch_pages()
        self.focus = self.cached_page[0]

    def fetch_pages(self):
        self.cached_page = []
        for p in self.fetched_page:
            article_list = self.server.article_manager.article_list(self.session_key, self.board_name, p, self.fetch_size)
            self.cached_page += article_list.hit
            self.last_page = article_list.last_page
            self.has_article = True
        if self.cached_page == []:
            self.cached_page = [{'new':'', 'number':'', 'author':'','title':_('No article found. Have a nice day.'),'date':'','hit':'','vote':''}]
            self.has_article = False

    def make_widget(self, article):
        if self.has_article:
            if self.session_key != 'guest':
                if article.deleted:
                    item = {'new':article.read_status, 'number':str(article.id), 'author':'', 'title':'Deleted article.', 'date':str(date.fromtimestamp(article.date).strftime('%m/%d')), 'hit':str(article.hit), 'vote':str(article.vote)}
                else:
                    item = {'new':article.read_status, 'number':str(article.id), 'author':article.author_username, 'title':article.title, 'date':str(date.fromtimestamp(article.date).strftime('%m/%d')), 'hit':str(article.hit), 'vote':str(article.vote)}
            else:
                if article.deleted:
                    item = {'number':str(article.id), 'author':'', 'title':'Deleted article.', 'date':str(date.fromtimestamp(article.date).strftime('%m/%d')), 'hit':str(article.hit), 'vote':str(article.vote)}
                else:
                    item = {'number':str(article.id), 'author':article.author_username, 'title':article.title, 'date':str(date.fromtimestamp(article.date).strftime('%m/%d')), 'hit':str(article.hit), 'vote':str(article.vote)}
        else:
            item = self.cached_page[0]
        return self.callback(item)

    def get_focus(self):
        return self.make_widget(self.focus), self.focus

    def set_focus(self, position):
        self.focus = position
        self._modified()

    def get_next(self, position):
        if not self.has_article:
            return None, None
        pos = self.cached_page.index(position)
        if pos < len(self.cached_page)-1:
            focus = self.cached_page[pos + 1]
        else:
            last_page = self.fetched_page[len(self.fetched_page)-1]
            if last_page >= self.last_page:
                return None, None
            self.fetched_page = [last_page, last_page + 1]
            self.fetch_pages()
            try:
                pos = self.cached_page.index(position)
                focus = self.cached_page[pos + 1]
            except:
                return None, None

        widget = self.make_widget(focus)
        return widget, focus

    def get_prev(self, position):
        if not self.has_article:
            return None, None
        pos = self.cached_page.index(position)
        if pos > 0:
            focus = self.cached_page[pos - 1]
        else:
            first_page = self.fetched_page[0]
            if first_page <= 1:
                return None, None
            self.fetched_page = [first_page-1, first_page]
            self.fetch_pages()
            try:
                pos = self.cached_page.index(position)
                focus = self.cached_page[pos - 1]
            except:
                return None, None

        widget = self.make_widget(focus)
        return widget, focus

# vim: set et ts=8 sw=4 sts=4:
