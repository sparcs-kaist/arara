# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator

import arara
import math


def get_various_info(request, r):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    page_no = request.GET.get('page_no', 1)
    r['num_new_message'] = 0
    r['num_message'] = 0
    r['next'] = 'a'
    r['prev'] = 'a'
    r['next_group'] = 'a'
    r['prev_group'] = 'a'
    r['nmpp'] = 10 #number of message per page
    r['mppp'] = 10 #number of pagegroup per page

    r['page_num'] = r['message_list'].pop()['last_page']
    r['message_num'] = len(r['message_list'])
    page_o = Paginator([x+1 for x in range(r['page_num'])],10)
    r['page_list'] = page_o.page(page_no).object_list

    if page_o.page(page_no).has_next():
        r['next_page_group'] = {'mark':r['next'], 'no':page_o.page(page_o.next_page_number()).start_index()}
        r['last_page'] = {'mark':r['next_group'], 'no':r['page_num']}
    if page_o.page(page_no).has_previous():
        r['prev_page_group'] = {'mark':r['prev'], 'no':page_o.page(page_o.previous_page_number()).end_index()}
        r['first_page'] = {'mark':r['prev_group'], 'no':1}
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

    r = {}
    r['next'] = 'a'
    r['prev'] = 'a'
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
