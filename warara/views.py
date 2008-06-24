# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.loader import render_to_string

def main(request):
    rendered = render_to_string('main.html',
               {'browser_title':'WebARAra',
                'arara_login':'로그인',
                'bbs_list': ['garbages'],
                'widget':'위젯',
                'today_best':'투베',
                'kaist_news':'카이스트 뉴스',
                'week_best':'윅베',
                'portal':'포탈공지',
                'banner':'배너'})
    return HttpResponse(rendered)

def list(request, bbs):
    rendered = render_to_string('list.html',
               {'browser_title':'WebARAra',
                   'arara_login':'로그인',
                   'bbs_list': ['garbage'],
                   'widget':'위젯',
                   'bbs_header':'garbage : 가비지',
                   'article_list':'글목록',
                   'menu':'글쓰기',
                   'pages':range(1, 11)})
    return HttpResponse(rendered)
