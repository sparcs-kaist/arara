# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
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

    message_list = Paginator(r['message_list'], r['nmpp'])
    page_list = Paginator(message_list.page_range, r['mppp'])
    pagegroup_no = math.ceil(float(r['page_no']) / r['mppp'])
    thispagegroup = page_list.page(pagegroup_no)
    r['message_list'] = message_list.page(r['page_no']).object_list
    r['page_list'] = page_list.page(pagegroup_no).object_list
    r['prev_page_group'] = {'mark':r['prev'], 'no':0}
    r['first_page'] = {'mark':r['prev_group'], 'no':0}
    r['next_page_group'] = {'mark':r['next'], 'no':0}
    r['last_page'] = {'mark':r['next_group'], 'no':0}
    
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
    r['message_list_type'] = 'inbox'
    r['person_type'] = 'sender'
    ret, r['message_list'] = server.messaging_manager.receive_list(sess)

    rendered = render_to_string('message/message_list.html', r)
    return HttpResponse(rendered)

def outbox(request):
    server = arara.get_server()
    sess = test_login()
    r = get_various_info(request)
    r['message_list_type'] = 'outbox'
    r['person_type'] = 'receiver'
    ret, r['message_list'] = server.messaging_manager.sent_list(sess)
    
    rendered = render_to_string('message/message_list.html', r)
    return HttpResponse(rendered)

def send(request):
    if request.POST:
        return send_(request)

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

    return HttpResponseRedirect(r['url'])

def read(request):
    server = arara.get_server()
    sess = test_login()

    r = get_various_info(request)
    msg_no = request.GET.get('msg_no', 3)
    msg_no = int(msg_no)
    list_type = request.POST.get('list_type', 'inbox')
    ret, r['message'] = server.messaging_manager.read_message(sess, msg_no)
    r['prev_message'] = {'mark':r['prev'], 'msg_no':''}
    r['next_message'] = {'mark':r['next'], 'msg_no':''}
    r['t_delete'] = 'delete'
    r['t_reply'] = ''
    r['t_list'] = 'list'
    r['t_deliever'] = 'deliever'

    if list_type == 'inbox':
        r['person_type'] = 'sender'
        r['person'] = r['message']['from']
        r['t_reply'] = 'reply'
    elif list_type == 'outbox':
        r['person_type'] = 'receiver'
        r['person'] = r['message']['to']
        r['t_reply'] = ''

    rendered = render_to_string('message/message_read.html', r)
    return HttpResponse(rendered)
