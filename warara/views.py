# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.loader import render_to_string

bbslist = ['KAIST', 'garbage']
widget = 'widget'
arara_login = 'login'

def intro(request):
    rendered = render_to_string('intro.html', {})
    return HttpResponse(rendered)

def main(request):
    todaybestlist = [{'title':'투베1', 'author':'쌀'},
            {'title':'투베2', 'author':'쌀'}]
    todaybest = render_to_string('listpanel.html',
            {'listname':'todaybest',
                'articles':todaybestlist})

    weekbestlist = [{'title':'윅베1', 'author':'쌀'},
            {'title':'윅베2', 'author':'쌀'}]
    weekbest = render_to_string('listpanel.html',
            {'listname':'weekbest',
                'articles':weekbestlist})

    portallist = [{'title':'포탈1', 'author':'쌀'},
            {'title':'포탈2', 'author':'쌀'}]
    portal = render_to_string('listpanel.html',
            {'listname':'portal',
                'articles':portallist})


    newslist = [{'title':'NEWS1', 'author':'쌀'},
            {'title':'NEWS2', 'author':'쌀'}]
    news = render_to_string('listpanel.html',
            {'listname':'news',
                'articles':newslist})

    rendered = render_to_string('main.html',
            {'today_best':todaybest,
                'kaist_news':news,
                'week_best':weekbest,
                'portal':portal,
                'banner':'배너'})
    return HttpResponse(rendered)

def modify(request, bbs, article_num):
    rendered = render_to_string('modify.html',
            {'bbs_list':bbslist,
                'widget':widget,
                'arara_login':arara_login,
                'bbs_header':bbs,
	        'article_number':article_num,
	        'article_subject':'글제목',
	        'article_content':'글내용'})
    return HttpResponse(rendered)

def read(request, bbs, no):
    rendered = render_to_string('read.html',
            {'bbs_list':bbslist,
                'widget':widget,
                'arara_login':arara_login,
                'bbsname':bbs,
                'bbs_header':'bbs_header',
                'articles':[{'no':'1', 'title':'title1', 'author':'author1', 'content':'content1'},
                    {'no':'2', 'title':'reply1', 'author':'author2', 'content':'content2'},
                    {'no':'3', 'title':'reply2', 'author':'author3', 'content':'content2'}]})
    return HttpResponse(rendered)

def list(request, bbs):
    articles = [{'no':1,'read_status':'N','title':'가나다','author':'조준희','date':'2008/06/24','hit':11,'vote':2,'content':'글내용'}]
    rendered = render_to_string('list.html',
            {'bbs_list':bbslist,
                'widget':widget,
                'arara_login':arara_login,
                'bbs_header':bbs,
                'article_list':articles,
                'menu':'write',
                'pages':range(1, 11)})
    return HttpResponse(rendered)

def write(request, bbs):
    rendered = render_to_string('write.html',
            {'bbs_list':bbslist,
                'widget':widget,
                'arara_login':arar_login,
                'bbs_header':bbs,
	        'article_subject':'article_subject',
	        'article_content':'article_content'}) 
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
    mtm_item['m_who']="sender"
    
    m_list=[]
    m_list.append({'checkbox':'checkbox', 'sender':'ssaljalu', 'msg_no':1,
	'receiver':'jacob', 'text':'Who are you', 'time':'08.06.26 18:51'})
    m_list_key=['checkbox', 'sender', 'text', 'time']
    m_list_value=[]
    m_list.append({'checkbox':'checkbox', "msg_no":2, "sender":"pipoket", 
	"receiver":"serialx","text": "polabear hsj", "time":"2008.02.13. 12:17:34"})

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

    def rim(m_num):
	mtm_item=copy.deepcopy(m.mtm_item)
	mtm_item['m_who']="sender"
	mtm_item['mr_reply']="reply"
	mtm_item['read_message']=mtm_item['m_list'][m_num]
	return render_to_string('read_message.html', mtm_item)
    rim=staticmethod(rim)

    def rom(m_num):
	mtm_item=copy.deepcopy(m.mtm_item)
	mtm_item['mr_reply']=""
	mtm_item['m_who']="receiver"
	mtm_item['read_message']=mtm_item['m_list'][m_num]
	return render_to_string('read_message.html', mtm_item)
    rom=staticmethod(rom)

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

def rim(request, m_num): #read_inbox_message
    m_num = int(m_num)
    rendered = m.rim(m_num)
    return HttpResponse(rendered)

def rom(request, m_num): #read_outbox_message
    m_num = int(m_num)
    rendered = m.rom(m_num)
    return HttpResponse(rendered)
