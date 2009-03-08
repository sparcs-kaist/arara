#!/usr/bin/python
from article_list_walker import *

class ArticleSearchWalker(ArticleListWalker):
    def __init__(self, session_key, board_name, callback, all_flag, query_dict):
        self.all_flag = all_flag
        self.query_dict = query_dict
        ArticleListWalker.__init__(self,session_key, board_name, callback)

    def fetch_pages(self):
        self.cached_page = []
        for p in self.fetched_page:
            article_list = self.server.search_manager.search(self.session_key, self.all_flag,
                    self.board_name, self.query_dict, p, self.fetch_size)
            self.cached_page += article_list['hit']
            self.last_page = article_list['last_page']
            self.has_article = True
        if self.cached_page == []:
            self.cached_page = [{'new':'', 'number':'', 'author':'','title':_('No article found. Have a nice day.'),'date':'','hit':'','vote':''}]
            self.has_article = False

# vim: set et ts=8 sw=4 sts=4:
