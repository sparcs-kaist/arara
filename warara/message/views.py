# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator

import arara
import math


def get_various_info(request, r):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    page_no = r['page_no']
    page_no = int(page_no)
    page_range_length = 10
    r['num_new_message'] = 0
    r['num_message'] = 0
    r['next'] = 'a'
    r['prev'] = 'a'
    r['next_group'] = 'a'
    r['prev_group'] = 'a'
    r['nmpp'] = 10 #number of message per page
    r['mppp'] = 10 #number of pagegroup per page

    page_group_no = math.ceil(float(page_no)/page_range_length)
    r['page_num'] = r['message_list'].pop()['last_page']
    r['message_num'] = len(r['message_list'])
    page_o = Paginator([x+1 for x in range(r['page_num'])], 10)
    r['page_list'] = page_o.page(page_group_no).object_list

    if page_o.page(page_group_no).has_next():
        r['next_page_group'] = {'mark':r['next'], 'no':page_o.page(page_o.page(page_group_no).next_page_number()).start_index()}
        r['last_page'] = {'mark':r['next_group'], 'no':r['page_num']}
    if page_o.page(page_group_no).has_previous():
        r['prev_page_group'] = {'mark':r['prev'], 'no':page_o.page(page_o.page(page_group_no).previous_page_number()).end_index()}
        r['first_page'] = {'mark':r['prev_group'], 'no':1}
    return r

def index(request):
    return HttpResponseRedirect("/message/inbox/")

def inbox(request):
    server = arara.get_server()
    r = {}
    sess = request.session["arara_session_key"]
    if request.GET.has_key('page_no'):
        page = request.GET['page_no']
    else:
        page = 1
    page_length = 20
    r['logged_in'] = True
    ret, r['message_list'] = server.messaging_manager.receive_list(sess, page, page_length)
    if not ret:
        page = int(page)
        while page>0:
            page -= 1
            ret, r['message_list'] = server.messaging_manager.receive_list(sess, page, page_length)
            if ret:
                break;
    r['page_no'] = page

    assert ret, r['message_list']
    r = get_various_info(request, r)
    r['message_list_type'] = 'inbox'
    r['person_type'] = 'sender'

    rendered = render_to_string('message/list.html', r)
    return HttpResponse(rendered)

def outbox(request):
    server = arara.get_server()
    r = {}
    sess = request.session["arara_session_key"]
    if request.GET.has_key('page_no'):
        page = request.GET['page_no']
    else:
        page = 1
    page_length = 20
    r['logged_in'] = True
    ret, r['message_list'] = server.messaging_manager.sent_list(sess, page, page_length)
    if not ret:
        page = int(page)
        while page>0:
            page -= 1
            ret, r['message_list'] = server.messaging_manager.receive_list(sess, page, page_length)
            if ret:
                break;
    r['page_no'] = page
    
    assert ret, r['message_list']
    r = get_various_info(request, r)
    r['message_list_type'] = 'outbox'
    r['person_type'] = 'receiver'
    
    rendered = render_to_string('message/list.html', r)
    return HttpResponse(rendered)

def send(request, msg_no=0):
    if request.method == 'POST':
        return send_(request)

    r = {}
    r['logged_in'] = True
    r['default_receiver'] = ''
    r['default_text'] = ''

    server = arara.get_server()
    sess = request.session["arara_session_key"]
    msg_no = int(msg_no)

    if msg_no:
        ret, message = server.messaging_manager.read_received_message(sess, msg_no)
        assert ret, message
        r['default_receiver'] = message['from']

    if request.GET.get('mutli', 0): #for test only
        multi = request.GET['multi']
        multi = int(multi)
        for i in range(multi):
            ret, message = server.messaging_manager.send_message(sess, 'mikkang', str(i))

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
    #assert ret, message

    if not ret:
        r['e'] = message
        if "ajax" in request.POST:
            return HttpResponse(message)
        rendered = render_to_string('message/error.html', r)
        return HttpResponse(rendered)

    if "ajax" in request.POST:
        return HttpResponse("Message send successful!")
    return HttpResponseRedirect(r['url'])

def read(request, message_list_type, message_id):
    server = arara.get_server()
    sess = request.session["arara_session_key"]

    r = {}
    r['logged_in'] = True
    r['next'] = 'a'
    r['prev'] = 'a'
    message_id = int(message_id)
    if message_list_type == 'inbox':
        ret, r['message'] = server.messaging_manager.read_received_message(sess, message_id)
    elif message_list_type == 'outbox':
        ret, r['message'] = server.messaging_manager.read_sent_message(sess, message_id)
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

def delete(request):
    server = arara.get_server()
    sess = request.session["arara_session_key"]
    ret, msg = 1, 1

    if request.POST.get('del_msg_no', 0):
        ret, msg = server.messaging_manager.delete_message(sess, int(request.POST.get('del_msg_no', 0)))
    elif request.method == "POST":
        for x in range(21): #need_modify
            del_msg_no = request.POST.get('ch_del_%s' % x, 0)
            if del_msg_no:
                del_msg_no = int(del_msg_no)
                ret, msg = server.messaging_manager.delete_message(sess, int(del_msg_no));
    assert ret, msg

    return HttpResponseRedirect("/message/%s/?page_no=%s" %
            (request.POST.get('message_list_type', 'inbox'),
                request.POST.get('page_no', 1)))
