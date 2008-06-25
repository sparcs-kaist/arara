# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.loader import render_to_string

def main(request):
    rendered = render_to_string('main.html',
               {'browser_title':'WebARAra',
                'arara_login':'로그인',
                'bbs_list': ['KAIST', 'garbage'],
                'widget':'위젯',
                'today_best':'투베',
                'kaist_news':'카이스트 뉴스',
                'week_best':'윅베',
                'portal':'포탈공지',
                'banner':'배너'})
    return HttpResponse(rendered)

def modify(request, bbs, article_num):
    rendered = render_to_string('modify.html',
	       {'browser_title':'WebARAra',
		   'arara_login':'login',
		   'bbs_list': ['KAIST', 'garbage'],
		   'widget':'widget',
		   'bbs_header':bbs,
		   'article_number':article_num,
		   'article_subject':'글제목',
		   'article_content':'글내용'})
    return HttpResponse(rendered)

def list(request, bbs):
    articles = [{'no':1,'read_status':'N','title':'가나다','author':'조준희','date':'2008/06/24','hit':11,'vote':2,'content':'글내용'}]
    rendered = render_to_string('list.html',
               {'browser_title':'WebARAra',
                   'arara_login':'로그인',
                   'bbs_list': ['KAIST', 'garbage'],
                   'widget':'위젯',
                   'bbs_header':bbs,
                   'article_list':articles,
                   'menu':'글쓰기',
                   'pages':range(1, 11)})
    return HttpResponse(rendered)

mtm_item={'mtm_item':['inbox', 'outbox', 'send', 'search user']}

def write_message(request):
    rendered = render_to_string('write_message.html', mtm_item)
    return HttpResponse(rendered)

def inbox_list(request):
    mtm_item['m_list']=[]
    rendered = render_to_string('inbox_list.html', mtm_item)
    return HttpResponse(rendered)
