# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse

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
    r['message_num'] = len(r['message_list'])
    r['page_no'] = float(r['page_no'])
    r['mppp'] = float(r['mppp'])
    r['max_message_list_text_length'] = 10
    r['pagegroup_no'] = math.ceil(r['page_no'] / r['mppp'])
    r['page_num'] = math.ceil(r['message_num'] / r['nmpp'])
    r['pagegroup_num'] = math.ceil(r['page_num'] / r['mppp'])
    r['next_page_group'] = {'mark':r['next'], 'no':int(r['pagegroup_no'] * r['mppp'] + 1)}
    r['prev_page_group'] = {'mark':r['prev'], 'no':int((r['pagegroup_no']-1) * r['mppp'])}
    r['first_page'] = {'mark':r['prev_group'], 'no':1}
    r['last_page'] = {'mark':r['next_group'], 'no':r['message_num']}
    r['message_list'].reverse()

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
    ret, r['message_list'] = server.messaging_manager.receive_list(sess)

    return r


def inbox(request):
    r = get_various_info(request)
    r['m_list_th'] = ['sender', 'text', 'time']
    r['m_list_key'] = ['from', 'message', 'sent_time']
    r['message_list_type'] = 'inbox'
    make_message_list(request, r)

    rendered = render_to_string('message/message_list.html', r)
    return HttpResponse(rendered)

def outbox(request):
    r = get_various_info(request)
    r['message_list_type'] = 'outbox'
    
    rendered = render_to_string('message/message_list.html', r)
    return HttpResponse(rendered)

def send(request):
    r = {}
    r['receiver'] = 'receiver'
    r['send'] = 'send'
    r['cancel'] = 'cancel'

    rendered = render_to_string('message/message_send.html', r)
    return HttpResponse(rendered)
