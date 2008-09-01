#!/usr/bin/python
import urwid
import xmlrpclib
from configuration import *

class ArticleListWalker(urwid.ListWalker):
    def __init__(self, session_key, board_name, callback):
	self.server = xmlrpclib.Server("http://%s:%s" % (XMLRPC_HOST, XMLRPC_PORT), use_datetime = True)
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
            result, article_list = self.server.article_manager.article_list(self.session_key, self.board_name, p, self.fetch_size)
            assert result, article_list
            self.cached_page += article_list['hit']
            self.last_page = article_list['last_page']

    def make_widget(self, article):
        if not article.has_key('read_status') and self.session_key != 'guest': 
            article['read_status'] = 'N'
        if self.session_key != 'guest':
            if article['deleted']:
                item = {'new':article['read_status'], 'number':str(article['id']), 'author':'', 'title':'Deleted article.', 'date':str(article['date'].strftime('%m/%d')), 'hit':str(article['hit']), 'vote':str(article['vote'])}
            else:
                item = {'new':article['read_status'], 'number':str(article['id']), 'author':article['author_username'], 'title':article['title'], 'date':str(article['date'].strftime('%m/%d')), 'hit':str(article['hit']), 'vote':str(article['vote'])}
        else:
            if article['deleted']:
                item = {'number':str(article['id']), 'author':'', 'title':'Deleted article.', 'date':str(article['date'].strftime('%m/%d')), 'hit':str(article['hit']), 'vote':str(article['vote'])}
            else:
                item = {'number':str(article['id']), 'author':article['author_username'], 'title':article['title'], 'date':str(article['date'].strftime('%m/%d')), 'hit':str(article['hit']), 'vote':str(article['vote'])}
        return self.callback(item)

    def get_focus(self):
        return self.make_widget(self.focus), self.focus

    def set_focus(self, position):
        self.focus = position
        self._modified()

    def get_next(self, position):
        pos = self.cached_page.index(position)
        if pos < len(self.cached_page)-1:
            try:
                focus = self.cached_page[pos + 1]
            except:
                return None, None
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
        pos = self.cached_page.index(position)
        if pos > 0:
            try:
                focus = self.cached_page[pos - 1]
            except:
                return None, None
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
