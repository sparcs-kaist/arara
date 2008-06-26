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

def write(request, bbs):
    rendered = render_to_string('write.html',
	       {'browser_title':'WebARAra',
		'arara_login':'로그인',
	        'bbs_list': ['KAIST', 'garbage'],
	        'widget':'widget',
	        'bbs_header':bbs,
	        'article_subject':'글제목',
	        'article_content':'글내용'}) 
    return HttpResponse(rendered)

import copy
class m: #message
    mtm_item={'mtm_item':[  #message top menu item
	{'name':'inbox', 'url':'inbox'},
	{'name':'outbox', 'url':'outbox'},
	{'name':'send', 'url':'send'},
	{'name':'search user', 'url':'msu'}]} 
    mtm_item['nmespp']=[20, 30, 50]
    mtm_item['m_opse']=['content', 'sender']
    mtm_item['num_new_m']=0
    mtm_item['num_m']=0
    
    m_list=[{'checkbox':'checkbox', 'sender':'ssaljalu', 'text':'Who are you', 'time':'08.06.26 18:51'}]
    m_list_key=['checkbox', 'sender', 'text', 'time']
    m_list_value=[]

    mtm_item['m_list']=m_list
    mtm_item['m_list_key']=m_list_key
    mtm_item['m_list_value']=m_list_value

    def mdl(mtm_item): #make data to list
	cm=copy.deepcopy(mtm_item) #copy of mtm_item

	for list in cm['m_list']:
	    cm['m_list_value'].insert(0,[])
	    for key in cm['m_list_key']:
		cm['m_list_value'][0].append(list.get(key))
	return cm
    mdl=staticmethod(mdl)

    def write():
	mtm_item=copy.deepcopy(m.mtm_item)
	return render_to_string('write_message.html', mtm_item)
    write = staticmethod(write)

    def inbox_list():
	mtm_item=copy.deepcopy(m.mtm_item)
	mtm_item=m.mdl(mtm_item)
	return render_to_string('inbox_list.html', mtm_item)
    inbox_list = staticmethod(inbox_list)

    def outbox_list():
	mtm_item=copy.deepcopy(m.mtm_item)
	mtm_item['m_list_key']=['checkbox', 'receiver', 'text', 'time']
	mtm_item=m.mdl(mtm_item)
	return render_to_string('outbox_list.html', mtm_item)
    outbox_list=staticmethod(outbox_list)

    def msu():
	mtm_item=copy.deepcopy(m.mtm_item)
	return render_to_string('m_s_user.html', mtm_item)
    msu=staticmethod(msu)

def write_message(request):
    rendered = m.write()
    return HttpResponse(rendered)

def inbox_list(request):
    rendered = m.inbox_list()
    return HttpResponse(rendered)

def outbox_list(request):
    rendered = m.outbox_list()
    return HttpResponse(rendered)

def msu(request): #message search user
    rendered = m.msu()
    return HttpResponse(rendered)
