# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.loader import render_to_string
import copy
import xmlrpclib
import sys
from math import *

server = xmlrpclib.Server("http://localhost:8000")

def getBoardList(request):
    #Get board list
    '''
    suc, ret = server.article_manager.board_list(request.session['arara_session'])
    if suc == True:
        boardList = ret
    else:
        boardList = "게시판 목록 읽기 실패/ 데이터베이스 오류"
    '''
    boardList = ['KAIST', 'garbage']
    return boardList

def getLoginPanel(request):
    if request.session.has_key('arara_session'):
        loginPanel = render_to_string('loggedin.html', {'nickname':getNickname(request)})
    else:
        loginPanel = render_to_string('loggedout.html', {})
    return loginPanel

def getMemberInfo(request):
    suc, ret = server.member_manager.get_info(request.session['arara_session'])
    if suc == True:
        request.session['info'] = ret

def getID(request):
    if request.session.has_key('info') == False:
        getMemberInfo(request)
    return request.session['info']['id']

def getNickname(request):
    if request.session.has_key('info') == False:
        getMemberInfo(request)
    return request.session['info']['nickname']

def delSession(request):
    if request.session.has_key('arara_session') == True:
        del request.session['arara_session']
    if request.session.has_key('info') == True:
        del request.session['info']

widget = 'widget'

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
    passwd = request.POST['password']
    ip = request.META['REMOTE_ADDR']
    suc, ret = server.login_manager.login(id, passwd, ip)
    if suc == True:
        request.session['arara_session'] = ret
        redirectURL = "/main/"
    else:
        redirectURL = "/?e=" + ret
    rendered = render_to_string('redirect.html', {'url':redirectURL})
    return HttpResponse(rendered)

def logout(request):
    suc, ret = server.login_manager.logout(request.session['arara_session'])
    delSession(request)
    if suc == True:
        delSession(request)
        redirectURL = request.META['HTTP_REFERER']
    else:
        redirectURL = request.META['HTTP_REFERER'] + "?e=" + ret
    rendered = render_to_string('redirect.html', {'url':redirectURL})
    return HttpResponse(rendered)

def main(request):
    boardList = getBoardList(request)
    loginPanel = getLoginPanel(request)

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
            {'bbs_list':boardList,
                'widget':widget,
                'arara_login':loginPanel,
                'today_best':todaybest,
                'kaist_news':news,
                'week_best':weekbest,
                'portal':portal,
                'banner':'배너',
                'msg':msg})
    return HttpResponse(rendered)

def modify(request, bbs, article_num):
    boardList = getBoardList(request)
    loginPanel = getLoginPanel(request)

    rendered = render_to_string('modify.html',
            {'bbs_list':boardList,
                'widget':widget,
                'arara_login':loginPanel,
                'bbs_header':bbs,
                'article_number':article_num,
                'article_subject':'글제목',
                'article_content':'글내용'})
    return HttpResponse(rendered)

def register(request):
    if request.POST.has_key('id') == True:
        suc, ret = server.member_manager.register(
                   {'id':request.POST['id'],
                    'password':request.POST['passwordFirst'],
                    'nickname':request.POST['nickname'],
                    'email':request.POST['email'],
                    'sig':request.POST['signature'],
                    'self_introduce':request.POST['self-introduction'],
                    'default_language':request.POST['language']})
        if suc == True:
            redirectURL = '/'
        else:
            redirectURL = '/?e=' + ret
        rendered = render_to_string('redirect.html', {'url':redirectURL})
    else:
        rendered = render_to_string('register.html', {})
    return HttpResponse(rendered)

def read(request, bbs, no):
    boardList = getBoardList(request)
    loginPanel = getLoginPanel(request)

    rendered = render_to_string('read.html',
            {'bbs_list':boardList,
                'widget':widget,
                'arara_login':loginPanel,
                'bbsname':bbs,
                'bbs_header':'bbs_header',
                'article':{'no':'1', 'title':'title1', 'author':'author1', 'content':'content1'},
                'replies':[{'no':'2', 'title':'reply1', 'author':'author2', 'content':'content2'},
                    {'no':'3', 'title':'reply2', 'author':'author3', 'content':'content2'}]})
    return HttpResponse(rendered)

def list(request, bbs):
    boardList = getBoardList(request)
    loginPanel = getLoginPanel(request)

    articles = [{'no':1,'read_status':'N','title':'가나다','author':'조준희','date':'2008/06/24','hit':11,'vote':2,'content':'글내용'}]
    rendered = render_to_string('list.html',
            {'bbs_list':boardList,
                'widget':widget,
                'arara_login':loginPanel,
                'bbs_header':bbs,
                'article_list':articles,
                'menu':'write',
                'pages':range(1, 11)})
    return HttpResponse(rendered)

def write(request, bbs):
    boardList = getBoardList(request)
    loginPanel = getLoginPanel(request)

    if request.POST.has_key('article_subject'):
        article = {'title':request.POST['article_subject'],
                   'author':getID(request),
                   'content':request.POST['article_content'],
                   'method':'web'}
        suc, ret = server.article_manager.write_article(request.session['arara_session'], bbs, article)
        if suc == True:
            redirectURL = '/read/' + bbs + '/' + ret + '/'
        else:
            redirectURL = '/write/' + bbs + '/?e=' + ret
        rendered = render_to_string('redirect.html', {'url':redirectURL})
    else:
        rendered = render_to_string('write.html',
            {'bbs_list':boardList,
                'widget':widget,
                'arara_login':loginPanel,
                'bbs':bbs,
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
    
    nmpp=10 #number of message per page
    mppp=10 #number of page per page
    
    mtm_item={'mtm_item':[  #message top menu item
        {'name':'inbox', 'url':'inbox/1/'},
        {'name':'outbox', 'url':'outbox/1/'},
        {'name':'send', 'url':'send'},
        {'name':'search user', 'url':'msu'}]} 
    mtm_item['nmespp']=[20, 30, 50]
    mtm_item['m_opse']=['content', 'sender']
    mtm_item['num_new_m']=0
    mtm_item['num_m']=0
    mtm_item['m_who']="sender"
    mtm_item['pvmli']="《 " #prev message list
    mtm_item['pvmte']="〈 " #prev message text
    mtm_item['nemte']="〉 " #next message text
    mtm_item['nemli']="》 " #next message list
    mtm_item['p_init']=mtm_item['pvmli'] #page_initial
    mtm_item['p_prev']=mtm_item['pvmte']
    mtm_item['p_next']=mtm_item['nemte']
    mtm_item['p_end']=mtm_item['nemli']
    
    m_list=[]
    m_list.append({'checkbox':'checkbox', 'sender':'ssaljalu', 'msg_no':10,
        'receiver':'jacob', 'text':'Who are you', 'time':'08.06.26 18:51'})
    m_list_key=['checkbox', 'sender', 'text', 'time']
    m_list_value=[]
    m_list.append({'checkbox':'checkbox', "msg_no":7, "sender":"pipoket", 
        "receiver":"serialx","text": "polabear hsj", "time":"2008.02.13. 12:17:34"})
    m_list.append({'checkbox':'checkbox', 'msg_no':int(9482), 'sender':'peremen',
	'receiver':'pv457', 'time':'08.07.03 14:35', 'text':'''
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right round
	you spin me right roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright roundright round
	'''})
    for k in range(700,1000):
	m_list.append({'checkbox':'checkbox', 'sender':'breadfish',
	    'receiver':'breadfish', 'time':'08.07.05 14:00',
	    'msg_no':k, 'text':''.join([str(k)]*20)})

    mtm_item['m_list']=m_list
    mtm_item['m_list_key']=m_list_key
    mtm_item['m_list_value']=m_list_value
    mtm_item['num_m']=len(mtm_item['m_list']) #number of message
    mtm_item['e']=''

    def m_sort(mtm_item): #message sort
        cm=copy.deepcopy(mtm_item)

        def get_no(m):
            return m['msg_no']
        cm.sort(key=get_no)
        return cm
    mtm_item['m_list']=m_sort(mtm_item['m_list'])

    @classmethod
    def pa_con(cls, p_no, mtm_item): #page_control page_no
	p_no=int(p_no)
	cm=copy.deepcopy(mtm_item)

	nmpp=cls.nmpp
	mppp=cls.mppp
	m_num=len(cm['m_list']) #message number
        p_num = ceil(float(m_num) / nmpp) #number of page
	p_list=[] #page list

	if p_num==0:
	    p_num+=1
	pg_no = ceil(float(p_no)/mppp) #page group no
	pg_num = ceil(float(p_num)/mppp)
	p_list=range(int(pg_no - 1) * mppp + 1, int(pg_no) * mppp + 1)
	if p_no>p_num:
	    raise IndexError
	if pg_no<=2:
	    cm['p_init']=''
	    if pg_no==1:
		cm['p_prev']=''
	if pg_no>=pg_num-1:
	    cm['p_end']=''
	    if pg_no==pg_num:
		cm['p_next']=''
		p_list = range(int(pg_no-1)*mppp+1, int(p_num+1))

	if m_num-(p_no*nmpp)<0 :
	    cm['m_list']=cm['m_list'][0:m_num-((p_no-1)*nmpp)]
	else:
	    cm['m_list'] = cm['m_list'][m_num-(p_no*nmpp):m_num-((p_no-1)*nmpp)]

	cm['p_list'] = p_list
	cm['p_no'] = p_no
	cm['un_p_prev'] = int(pg_no-2) * mppp + 1 #urllink number of p_prev mark
	cm['un_p_next'] = int(pg_no) * mppp + 1
	cm['un_p_end'] = int(p_num)
	return cm

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

    def indexof(m_list, m_no): #search the index of the m_numth article in m_list
	for i, arti in enumerate(m_list):
	    if arti['msg_no']==int(m_no):
		return i
	return 'e'
    indexof=staticmethod(indexof)

    @classmethod
    def message_read_page_move(cls, m_no):
	cm=m.mtm_item
	nmpp=cls.nmpp
	m_ino = m.indexof(cm['m_list'], m_no) #message_indexno
	cm['mrpv']={}

	cm['mrpv']['pvmli']={'mark':cm['pvmli'], 'no':0, 'urln':''}
	cm['mrpv']['pvmte']={'mark':cm['pvmte'], 'no':1, 'urln':''}
	cm['mrpv']['nemte']={'mark':cm['nemte'], 'no':2, 'urln':''}
	cm['mrpv']['nemli']={'mark':cm['nemli'], 'no':3, 'urln':''}

	if m_ino>0:
	    cm['mrpv']['pvmte']['urln']=cm['m_list'][m_ino-1]['msg_no']
	    cm['mrpv']['pvmli']['urln']=cm['m_list'][0]['msg_no']
	    if m_ino>=nmpp:
		cm['mrpv']['pvmli']['urln']=cm['m_list'][m_ino-nmpp]['msg_no']
	if m_ino<cm['num_m']-1 :
	    cm['mrpv']['nemte']['urln']=cm['m_list'][m_ino+1]['msg_no']
	    cm['mrpv']['nemli']['urln']=cm['m_list'][cm['num_m']-1]['msg_no']
	    if m_ino<cm['num_m']-nmpp:
		cm['mrpv']['nemli']['urln']=cm['m_list'][m_ino+nmpp]['msg_no']
	
	def get_no(mrpv):
	    return mrpv['no']
	cm['mrpv']=cm['mrpv'].values()
	cm['mrpv'].sort(key=get_no)

    def write():
        mtm_item=copy.deepcopy(m.mtm_item)
        return render_to_string('write_message.html', mtm_item)
    write = staticmethod(write)

    def inbox_list(num_page):
        mtm_item=copy.deepcopy(m.mtm_item)
	mtm_item['readtype']="rim"
	mtm_item['listtype']='inbox'
	try:
	    mtm_item=m.pa_con(p_no=num_page, mtm_item=mtm_item)
	except IndexError:
	    mtm_item['e']='그런페이지없어'
	    return render_to_string('error.html', mtm_item)
        mtm_item=m.mdl(mtm_item)
        return render_to_string('inbox_list.html', mtm_item)
    inbox_list = staticmethod(inbox_list)

    def outbox_list(num_page):
        mtm_item=copy.deepcopy(m.mtm_item)
        mtm_item['m_list_key']=['checkbox', 'receiver', 'text', 'time']
	mtm_item['readtype']="rom"
	mtm_item['listtype']='outbox'
	try:
	    mtm_item=m.pa_con(p_no=num_page, mtm_item=mtm_item)
	except IndexError:
	    mtm_item['e']='그런페이지없어'
	    return render_to_string('error.html', mtm_item)
        mtm_item=m.mdl(mtm_item)
        return render_to_string('outbox_list.html', mtm_item)
    outbox_list=staticmethod(outbox_list)

    def msu():
        mtm_item=copy.deepcopy(m.mtm_item)
        return render_to_string('m_s_user.html', mtm_item)
    msu=staticmethod(msu)

    def rim(m_no):
	try:
	    m.message_read_page_move(m_no)
	except TypeError:
	    mtm_item['e']='메세지가 ㅇ벗습니다'
	except IndexError:
	    mtm_item['e']='없는 인덱스 참조'
	except:
	    mtm_item['e']='unknown error'

        mtm_item=copy.deepcopy(m.mtm_item)
        mtm_item['m_who']="sender"
        mtm_item['mr_reply']="reply"
	mtm_item['readtype']="rim"

	try:
            mtm_item['read_message']=mtm_item['m_list'][m.indexof(mtm_item['m_list'], m_no)]
	except TypeError:
	    mtm_item['e']='그런메세지없어'
	    return render_to_string('error.html', mtm_item)
        return render_to_string('read_message.html', mtm_item)
    rim=staticmethod(rim)

    def rom(m_no):
	try:
	    m.message_read_page_move(m_no)
	except TypeError:
	    mtm_item['e']='메세지가 ㅇ벗습니다'
	except IndexError:
	    mtm_item['e']='없는 인덱스 참조'
	except:
	    mtm_item['e']='unknown error'

	mtm_item=copy.deepcopy(m.mtm_item)
        mtm_item['mr_reply']=""
        mtm_item['m_who']="receiver"
	mtm_item['readtype']="rom"

	try:
	    mtm_item['read_message']=mtm_item['m_list'][m.indexof(mtm_item['m_list'], m_no)]
	except TypeError:
	    return render_to_string('error.html', mtm_item)
        return render_to_string('read_message.html', mtm_item)
    rom=staticmethod(rom)

def write_message(request):
    rendered = m.write()
    return HttpResponse(rendered)

def inbox_list(request, num_page):
    rendered = m.inbox_list(num_page)
    return HttpResponse(rendered)

def outbox_list(request, num_page):
    rendered = m.outbox_list(num_page)
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

class h: #help
    htm_item={'htm_item':[
        {'name':'shortcut', 'url':'shortcut'},
        {'name':'user agreement', 'url':'agreement'}]}
    
    def short():
        htm_item=copy.deepcopy(h.htm_item)
        return render_to_string('help_frame.html', htm_item)
    short=staticmethod(short)
    
    def agree():
        htm_item=copy.deepcopy(h.htm_item)
        return render_to_string('help_agreement.html', htm_item)
    agree=staticmethod(agree)
    
def shortcut(request):
    rendered = h.short()
    return HttpResponse(rendered)

def agreement(request):
    rendered = h.agree()
    return HttpResponse(rendered)

# vim: set et ts=8 sw=4 sts=4
