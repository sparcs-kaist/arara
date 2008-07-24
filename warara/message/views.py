# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator

import arara
import math


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

def get_various_info(request, r):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    r['num_new_message'] = 0
    r['num_message'] = 0
    r['next'] = 'a'
    r['prev'] = 'a'
    r['next_group'] = 'a'
    r['prev_group'] = 'a'
    r['nmpp'] = 10 #number of message per page
    r['mppp'] = 10 #number of pagegroup per page

    r['page_num'] = r['message_list'].pop()

    return r

def index(request):
    return HttpResponseRedirect("/message/inbox/")

def inbox(request):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    r={} #render item
    ret, r['message_list'] = server.messaging_manager.receive_list(sess)
    assert ret, r['message_list']
    r = get_various_info(request, r)
    r['message_list_type'] = 'inbox'
    r['person_type'] = 'sender'

    rendered = render_to_string('message/list.html', r)
    return HttpResponse(rendered)

def outbox(request):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    r={}
    ret, r['message_list'] = server.messaging_manager.sent_list(sess)
    assert ret, r['message_list']
    r = get_various_info(request, r)
    r['message_list_type'] = 'outbox'
    r['person_type'] = 'receiver'
    
    rendered = render_to_string('message/list.html', r)
    return HttpResponse(rendered)

def send(request, msg_no=0):
    if request.POST:
        return send_(request)

    r = {}
    r['default_receiver'] = ''
    r['default_text'] = ''

    server = arara.get_server()
    sess = request.session["arara_session_key"]
    msg_no = int(msg_no)

    if msg_no:
        ret, message = server.messaging_manager.read_message(sess, msg_no)
        assert ret, message
        r['default_receiver'] = message['from']
        r['default_text'] = message['message']

    rendered = render_to_string('message/send.html', r)
    return HttpResponse(rendered)

def send_(request):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    r = {}
    r['url'] = '/message/send'
    
    receiver = request.POST.get('receiver', '')
    text = request.POST.get('text', '')

    ret, message = server.messaging_manager.send_message(sess, receiver, text)
    assert ret, message

    if not ret:
        r['e'] = mes
        rendered = render_to_string('message/error.html', r)
        return HttpResponse(rendered)

    return HttpResponseRedirect(r['url'])

def read(request, message_list_type, message_id):
    server = arara.get_server()
    sess = request.session["arara_session_key"]

    r = get_various_info(request)
    message_id = int(message_id)
    ret, r['message'] = server.messaging_manager.read_message(sess, message_id)
    assert ret, r['message']

    r['prev_message'] = {'mark':r['prev'], 'msg_no':''}
    r['next_message'] = {'mark':r['next'], 'msg_no':''}
    r['message_id'] = message_id

    if message_list_type == 'inbox':
        r['person_type'] = 'sender'
        r['person'] = r['message']['from']
    elif message_list_type == 'outbox':
        r['person_type'] = 'receiver'
        r['person'] = r['message']['to']

    rendered = render_to_string('message/read.html', r)
    return HttpResponse(rendered)
