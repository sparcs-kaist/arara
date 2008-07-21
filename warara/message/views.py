# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.paginator import Paginator

import arara
import math

def test_login():
    server = arara.get_server()
    ret, sess = server.login_manager.login('breadfish', 'breadfish', '127.0.0.1')
    assert ret == True
    return sess

def make_message_list(request, r):
    r['page_no'] = request.POST.get('page_no', 1)
    r['page_no'] = int(r['page_no'])
    r['max_message_list_text_length'] = 10
    r['message_list'].reverse()
    r['message_num'] = len(r['message_list'])
    '''
    r['page_no'] = float(r['page_no'])
    r['mppp'] = float(r['mppp'])
    r['pagegroup_no'] = math.ceil(r['page_no'] / r['mppp'])
    r['page_num'] = math.ceil(float(r['message_num']) / r['nmpp'])
    r['pagegroup_num'] = math.ceil(r['page_num'] / r['mppp'])
    r['next_page_group'] = {'mark':r['next'], 'no':int(r['pagegroup_no'] * r['mppp'] + 1)}
    r['prev_page_group'] = {'mark':r['prev'], 'no':int((r['pagegroup_no']-1) * r['mppp'])}
    r['first_page'] = {'mark':r['prev_group'], 'no':1}
    r['last_page'] = {'mark':r['next_group'], 'no':r['message_num']}

    if r['page_no']==r['page_num']:
        r['message_list'] = r['message_list'][int((r['page_no'] - 1) * r['nmpp']) 
            : int(r['message_num'] - 1)]
    else:
        r['message_list'] = r['message_list'][int((r['page_no'] - 1) * r['nmpp']) 
            : int(r['page_no'] * r['nmpp'])]

    if r['pagegroup_no'] == r['pagegroup_num']:
        r['page_list'] = range(int((r['pagegroup_no'] - 1) * r['nmpp'] + 1) 
            , int(r['page_num'] + 1))
        r['next_page_group']['no'] = 0
        r['last_page']['no'] = 0
    else:
        r['page_list'] = range(int((r['pagegroup_no'] - 1) * r['nmpp'] + 1)
            , int(r['pagegroup_no'] * r['nmpp'] + 1))

    if r['pagegroup_no'] == 1 :
        r['prev_page_group']['no'] = 0
        r['first_page']['no'] = 0
    '''

    message_list = Paginator(r['message_list'], r['nmpp'])
    page_list = Paginator(message_list.page_range, r['mppp'])
    pagegroup_no = math.ceil(float(r['page_no']) / r['mppp'])
    thispagegroup = page_list.page(pagegroup_no)
    r['message_list'] = message_list.page(r['page_no']).object_list
    r['page_list'] = page_list.page(pagegroup_no).object_list
    r['prev_page_group'] = {}
    r['first_page'] = {}
    r['next_page_group'] = {}
    r['last_page'] = {}
    
    if thispagegroup.has_previous():
        r['prev_page_group'] = {'mark':r['prev'], 'no':
                page_list.page(thispagegroup.previous_page_number()).end_index()}
        r['first_page'] = {'mark':r['prev_group'], 'no':1}
    if thispagegroup.has_next():
        r['next_page_group'] = {'mark':r['next'], 'no':
                page_list.page(thispagegroup.next_page_number()).start_index()}
        r['last_page'] = {'mark':r['next_group'], 'no':
                page_list.page(page_list.num_pages).end_index()}

    for i, message in enumerate(r['message_list']):
        if len(message['message'])>r['max_message_list_text_length'] :
            message['message'] = {
                    'read_status':message['read_status'],
                    'text': ''.join([message['message'][0:r['max_message_list_text_length']],'...']),
                    'msg_no':message['msg_no']}
        else:
            message['message'] = {
                    'read_status':message['read_status'],
                    'text':message['message'],
                    'msg_no':message['msg_no']}
        message['sent_time'] = {'time':message['sent_time']}
        
        r['message_list'][i] = []
        for key in r['m_list_key']:
            r['message_list'][i].append(message[key])

def get_various_info(request):
    server = arara.get_server()
    sess = test_login()
    r = {}  # render_item
    r['num_new_message'] = 0
    r['num_message'] = 0
    r['next'] = 'a'
    r['prev'] = 'a'
    r['next_group'] = 'a'
    r['prev_group'] = 'a'
    r['nmpp'] = 10 #number of message per page
    r['mppp'] = 10 #number of pagegroup per page

    return r


def inbox(request):
    server = arara.get_server()
    sess = test_login()
    r = get_various_info(request)
    r['m_list_th'] = ['sender', 'text', 'time']
    r['m_list_key'] = ['from', 'message', 'sent_time']
    r['message_list_type'] = 'inbox'
    ret, r['message_list'] = server.messaging_manager.receive_list(sess)
    make_message_list(request, r)

    rendered = render_to_string('message/message_list.html', r)
    return HttpResponse(rendered)

def outbox(request):
    server = arara.get_server()
    sess = test_login()
    r = get_various_info(request)
    r['m_list_th'] = ['receiver', 'text', 'time']
    r['m_list_key'] = ['to', 'message', 'sent_time']
    r['message_list_type'] = 'outbox'
    ret, r['message_list'] = server.messaging_manager.sent_list(sess)
    make_message_list(request, r)
    
    rendered = render_to_string('message/message_list.html', r)
    return HttpResponse(rendered)

def send(request):
    r = {}
    r['default_receiver'] = ''
    r['default_text'] = ''
    r['t_receiver'] = 'receiver' #template_receiver
    r['t_send'] = 'send'
    r['t_cancel'] = 'cancel'
    r['t_receiver_info'] = 'distinguish receiver by space up to 10 people'

    rendered = render_to_string('message/message_send.html', r)
    return HttpResponse(rendered)

def send_(request):
    server = arara.get_server()
    sess = test_login()
    r = {}
    r['url'] = '/message/send'
    
    receiver = request.POST.get('receiver', '')
    text = request.POST.get('text', '')

    server.messaging_manager.send_message(sess, receiver, text)

    rendered = render_to_string('message/redirect.html', r)
    return HttpResponse(rendered)
