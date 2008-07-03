# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.loader import render_to_string
import copy
import xmlrpclib

#server = xmlrpclib.Server("xmlrpcserver")

'''
#Get board list
suc, ret = board_list(request.session['arara_session'])
if suc == True:
    bbslist = ret
else:
    bbslist = "게시판 목록 읽기 실패/ 데이터베이스 오류"
'''
bbslist = ['KAIST', 'garbage']

widget = 'widget'
arara_login = 'login'

def errormsg(e):
    if e == "WRONG_ID":
        msg = "그런 아이디 없어요"
    elif e == "WRONG_PASSWORD":
        msg = "비밀번호 틀렸어요"
    elif e == "DATABASE_ERROR":
        msg = "데이터베이스 에러"
    elif e == "NOT_LOGGEDIN":
        msg = "이미 로그아웃되었습니다"
    else:
        msg = ""
    return msg
    
def intro(request):
    msg = errormsg(request.GET.get('e', ""))
    rendered = render_to_string('intro.html', {'msg':msg})
    return HttpResponse(rendered)

def login(request):
    id = request.POST['id']
    passwd = request.POST['passwd']
    ip = request.META['REMOTE_ADDR']
    suc, ret = server.login_manager.login(id, passwd, ip)
    if suc == True:
        request.session['arara_session'] = ret
        redirect_url = "/main/"
    else:
        redirect_url = "/?e=" + ret
    rendered = render_to_string('redirect.html', {'url':redirect_url})
    return HttpResponse(rendered)

def logout(request):
    suc, ret = xmlrpclib.Server(xmlrpcserver)
    if suc == True:
        del request.session['arara_session']
        redirect_url = request.META['REFERER']
    else:
        redirect_url = request.META['REFERER'] + "/?e=" + ret
    return HttpResponse(request.session['arara_session'])

def main(request):
    msg = errormsg(request.GET.get('e', ""))

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
            {'bbs_list':bbslist,
                'widget':widget,
                'arara_login':arara_login,
                'today_best':todaybest,
                'kaist_news':news,
                'week_best':weekbest,
                'portal':portal,
                'banner':'배너',
                'msg':msg})
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
                'article':{'no':'1', 'title':'title1', 'author':'author1', 'content':'content1'},
                'replies':[{'no':'2', 'title':'reply1', 'author':'author2', 'content':'content2'},
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
                'arara_login':arara_login,
                'bbs_header':bbs,
	        'article_subject':'article subject',
	        'article_content':'article content',
		'boardname':[{'name':'--board--'},
		    {'name':'KAIST'},
		    {'name':'garbages'},
		    {'name':'food'},
		    {'name':'abroad'},
		    {'name':'love'},
		    {'name':'foreigner'},
		    {'name':'filmspecial'}]}) 
    return HttpResponse(rendered)

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
    m_list.append({'checkbox':'checkbox', 'sender':'ssaljalu', 'msg_no':0,
	'receiver':'jacob', 'text':'Who are you', 'time':'08.06.26 18:51'})
    m_list_key=['checkbox', 'sender', 'text', 'time']
    m_list_value=[]
    m_list.append({'checkbox':'checkbox', "msg_no":1, "sender":"pipoket", 
	"receiver":"serialx","text": "polabear hsj", "time":"2008.02.13. 12:17:34"})

    mtm_item['m_list']=m_list
    mtm_item['m_list_key']=m_list_key
    mtm_item['m_list_value']=m_list_value

    def m_sort(mtm_item): #message sort
	cm=copy.deepcopy(mtm_item)

	def get_no(m):
	    return m['msg_no']
	cm.sort(key=get_no)
	return cm
    m_sort=staticmethod(m_sort)

    def mdl(m_list): #make data to list
	cm=copy.deepcopy(m_list) #copy of mtm_item

	for list in cm['m_list']:
	    cm['m_list_value'].insert(0,[])
	    for key in cm['m_list_key']:
		if key=='text':
		    lm=10 #length limit
		    if len(list.get(key))>lm:
			list[key]=''.join([list.get(key)[0:lm], '...'])
			cm['m_list_value'][0].append({ 'key':key, 'value':list[key], 'msg_no':list.get('msg_no')})
			continue
		cm['m_list_value'][0].append(list.get(key))
	return cm
    mdl=staticmethod(mdl)

    def indexof(m_list, m_num): #search the index of the m_numth article in m_list
	for i, arti in enumerate(m_list):
	    if arti['msg_no']==m_num:
		return i
	return None
    indexof=staticmethod(indexof)

    def write():
	mtm_item=copy.deepcopy(m.mtm_item)
	return render_to_string('write_message.html', mtm_item)
    write = staticmethod(write)

    def inbox_list():
	mtm_item=copy.deepcopy(m.mtm_item)
	mtm_item['m_list']=m.m_sort(mtm_item['m_list'])
	mtm_item=m.mdl(mtm_item)
	return render_to_string('inbox_list.html', mtm_item)
    inbox_list = staticmethod(inbox_list)

    def outbox_list():
	mtm_item=copy.deepcopy(m.mtm_item)
	mtm_item['m_list']=m.m_sort(mtm_item['m_list'])
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
	mtm_item['read_message']=mtm_item['m_list'][m.indexof(mtm_item['m_list'], m_num)]
	return render_to_string('read_message.html', mtm_item)
    rim=staticmethod(rim)

    def rom(m_num):
	mtm_item=copy.deepcopy(m.mtm_item)
	mtm_item['mr_reply']=""
	mtm_item['m_who']="receiver"
	mtm_item['read_message']=mtm_item['m_list'][m.indexof(mtm_item['m_list', m_num)]
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

class b: #blacklist
    btm_item={'btm_item':[
	{'name':'My page', 'url':'mypage'},
	{'name':'Add blacklist', 'url':'add'}]}
    b_list_h=['ID','block_article','block_message']
    b_list=[]
    b_list.append({'ID':'MyungBakLee','block_article':'hi','block_message':'hi'})
    b_list.append({'ID':'SerialxIsPolarBear','block_article':'hi','block_message':'hi'})
    btm_item['b_list_h']=b_list_h
    btm_item['b_list']=b_list
    
    def black():
	btm_item=copy.deepcopy(b.btm_item)
	return render_to_string('blacklist.html', btm_item)
    black=staticmethod(black)

    def add():
	btm_item=copy.deepcopy(b.btm_item)
	return render_to_string('add_blacklist.html', btm_item)
    add=staticmethod(add)

def blacklist(request):
    rendered = b.black()
    return HttpResponse(rendered)

def add_black(request):
    rendered = b.add()
    return HttpResponse(rendered)
