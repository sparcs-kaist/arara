#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget
import listview

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

class ara_list_article(ara_form):
    def __init__(self, parent, session_key = None, board_name = None):
        self.board_name = board_name
        ara_form.__init__(self, parent, session_key)

    def keypress(self, size, key):
        key = key.strip()
        mainpile_focus = self.mainpile.get_focus()
        if key == "enter":
            # self.boardlist.get_body().get_focus()[0].w.w.widget_list : 현재 활성화된 항목
            article_id  = int(self.articlelist.get_body().get_focus()[0].w.w.widget_list[0].get_text()[0])
            if self.hasarticle:
                self.parent.change_page("read_article", {'session_key':self.session_key, 'board_name':self.board_name, 'article_id':article_id})
        elif key == 'w':
            self.parent.change_page('post_article', {'session_key':self.session_key, 'board_name':self.board_name, 'mode':'post', 'article_id':''})
        elif key == 'q':
            self.parent.change_page("main", {'session_key':self.session_key})
        else:
            self.mainpile.keypress(size, key)

    def __initwidgets__(self):
	self.header = urwid.Filler(urwid.Text(u"ARA: Article list",align='center'))
        self.header = urwid.AttrWrap(self.header, 'reversed')
        self.infotext1 = urwid.Filler(urwid.Text("(N)ext/(P)revious Page (n)ext/(p)revious article (Number+Enter) Jump to article"))
        self.infotext2 = urwid.Filler(urwid.Text("(Enter,space) Read (w)rite (f)ind (/)Find next (?) Find previous (h)elp (q)uit"))

        articles = self.server.article_manager.article_list(self.session_key, self.board_name)
        articles = articles[1]
        itemlist = []
        if len(articles) <= 1:
            itemlist += [{'new':'', 'number':'', 'author':'','title':'No article found. Have a nice day.','date':'','hit':'','vote':''}]
            self.hasarticle = False
        else:
            for article in articles:
                if article.has_key('last_page'):
                    self.last_page = article['last_page']
                    continue
                itemlist += [{'new':'N', 'number':str(article['id']), 'author':article['author_username'], 'title':article['title'],
                    'date':str(article['date'].strftime('%m/%d')), 'hit':str(article['hit']), 'vote':str(article['vote'])}]
            self.hasarticle = True
        header = {'new':'N', 'number':'#', 'author':'Author', 'title':'Title', 'date':'Date', 'hit':'Hit', 'vote':'Vote'}

        self.articlelist = listview.get_view(itemlist, header, articlelist_rowitem)

        content = [('fixed',1, self.header),('fixed',1,self.infotext1),('fixed',1,self.infotext2),self.articlelist,]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_list_article().main()

# vim: set et ts=8 sw=4 sts=4:
