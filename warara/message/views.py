# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator

import math
import warara
import datetime

from arara_thrift.ttypes import *
from warara import warara_middleware

def get_various_info(request, r):
    server = warara_middleware.get_server()
    sess, _ = warara.check_logged_in(request)
    page_no = r['page_no']
    page_no = int(page_no)
    page_range_length = 10
    r['next'] = 'a'
    r['prev'] = 'a'
    r['next_group'] = 'a'
    r['prev_group'] = 'a'
    r['nmpp'] = 10 #number of message per page
    r['mppp'] = 10 #number of pagegroup per page

    page_group_no = math.ceil(float(page_no)/page_range_length)
    r['page_num'] = r['message_result'].last_page
    r['num_message'] = r['message_result'].results
    page_o = Paginator([x+1 for x in range(r['page_num'])], 10)
    if page_o.num_pages < page_group_no:
        page_group_no = page_o.num_pages
    r['page_list'] = page_o.page(page_group_no).object_list

    if page_o.page(page_group_no).has_next():
        r['next_page_group'] = {'mark':r['next'], 'no':page_o.page(page_o.page(page_group_no).next_page_number()).start_index()}
        r['last_page'] = {'mark':r['next_group'], 'no':r['page_num']}
    if page_o.page(page_group_no).has_previous():
        r['prev_page_group'] = {'mark':r['prev'], 'no':page_o.page(page_o.page(page_group_no).previous_page_number()).end_index()}
        r['first_page'] = {'mark':r['prev_group'], 'no':1}

    r['message_no_strlist'] = ''
    for message in r['message_list']:
        r['message_no_strlist'] = '|'.join([r['message_no_strlist'], str(message.id)])

    r['page_length_list'] = [5, 10, 20]
    r['time_now'] = datetime.datetime.now()

    for i, message in enumerate(r['message_list']):
        if message.sent_time.strftime('%Y%m%d') == r['time_now'].strftime('%Y%m%d'):
            r['message_list'][i].time = message.sent_time.strftime('%H:%M:%S')
        else:
            r['message_list'][i].time = message.sent_time.strftime('%Y/%m/%d')

    return r

@warara.wrap_error
def index(request):
    return HttpResponseRedirect("/message/inbox/")

@warara.wrap_error
def inbox(request):
    server = warara_middleware.get_server()
    r = {}
    sess, _ = warara.check_logged_in(request)
    page = request.GET.get('page_no', 1);
    r['logged_in'] = True
    r['page_no'] = int(page)
    page_length = request.GET.get('page_length', 10)
    page_length = int(page_length)
    try:
        # XXX combacsa: Why use try - except?
        r['message_result'] = server.messaging_manager.receive_list(sess, page, page_length)
    except NotLoggedIn:
        raise NotLoggedIn()
    except Exception:
        page = int(page)
        while page>0:
            try:
                r['message_result'] = server.messaging_manager.receive_list(sess, page, page_length)
                break;
            except Exception:
                page -= 1
        if page <= 0:
            raise InvalidOperation("No nonpositive page in Message")
    if 'message_result' in r:
        for message in r['message_result'].hit:
            message.sent_time = datetime.datetime.fromtimestamp(message.sent_time)
    r['message_list'] = r['message_result'].hit
    r = get_various_info(request, r)
    r['num_new_message'] = r['message_result'].new_message_count
    r['page_length'] = int(page_length)
    r['message_list_type'] = 'inbox'
    r['person_type'] = 'sender'

    rendered = render_to_string('message/list.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def outbox(request):
    # XXX Combacsa: What about merging inbox & outbox alltogether?
    server = warara_middleware.get_server()
    r = {}
    sess, _ = warara.check_logged_in(request)
    if request.GET.has_key('page_no'):
        page = request.GET['page_no']
    else:
        page = 1
    r['logged_in'] = True
    r['page_no'] = int(page)
    page = int(page) # XXX 2010.05.15. 땜빵
    page_length = request.GET.get('page_length', 10)
    page_length = int(page_length)
    try:
        r['message_result'] = server.messaging_manager.sent_list(sess, page, page_length)
    except NotLoggedIn:
        raise NotLoggedIn()
    except Exception:
        page = int(page)
        while page>0:
            page -= 1
            try:
                r['message_result'] = server.messaging_manager.sent_list(sess, page, page_length)
            except Exception:
                break;
    for message in r['message_result'].hit:
        message.sent_time = datetime.datetime.fromtimestamp(message.sent_time)
    r['message_list'] = r['message_result'].hit
    r = get_various_info(request, r)
    r['page_length'] = int(page_length)
    r['message_list_type'] = 'outbox'
    r['person_type'] = 'receiver'
    
    rendered = render_to_string('message/list.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def send(request, msg_no=0):
    if request.method == 'POST':
        return send_(request)

    r = {}
    r['logged_in'] = True
    r['default_receiver'] = ''
    r['default_text'] = ''

    server = warara_middleware.get_server()
    sess, _ = warara.check_logged_in(request)
    msg_no = int(msg_no)

    if msg_no:
        message = server.messaging_manager.read_received_message(sess, msg_no)
        r['default_receiver'] = message.from_

    if request.GET.get('multi', 0): #for test only
        multi = request.GET['multi']
        multi = int(multi)
        rc = request.GET.get('rc', 'SYSOP')
        con = request.GET.get('con', 'almond chocoball')
        for i in range(multi):
            message = server.messaging_manager.send_message(sess, rc, con)
        return HttpResponseRedirect('/message/outbox/')

    rendered = render_to_string('message/send.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def send_(request):
    server = warara_middleware.get_server()
    sess, _ = warara.check_logged_in(request)
    r = {}
    
    receiver = request.POST.get('receiver', '')
    text = request.POST.get('text', '')
    receiver_type = request.POST.get('receiver_type', 'username')
    if receiver_type == "nickname":
        server.messaging_manager.send_message_by_nickname(sess, receiver, text)
    else:
        server.messaging_manager.send_message_by_username(sess, receiver, text)

    if "ajax" in request.POST:
        return HttpResponse(1)
    r['url'] = '/message/outbox'
    return HttpResponseRedirect(r['url'])

@warara.wrap_error
def read(request, message_list_type, message_id):
    server = warara_middleware.get_server()
    sess, _ = warara.check_logged_in(request)

    r = {}
    r['logged_in'] = True
    r['page_length'] = request.GET.get('page_length', 10)
    r['page_no'] = request.GET.get('page_no', 1)
    message_id = int(message_id)
    if message_list_type == 'inbox':
        r['message'] = server.messaging_manager.read_received_message(sess, message_id)
    elif message_list_type == 'outbox':
        r['message'] = server.messaging_manager.read_sent_message(sess, message_id)
    r['message'].sent_time = datetime.datetime.fromtimestamp(r['message'].sent_time)

    r['message_id'] = message_id
    r['message_list_type'] = message_list_type

    if message_list_type == 'inbox':
        r['person_type'] = 'sender'
        r['person'] = r['message'].from_
    elif message_list_type == 'outbox':
        r['person_type'] = 'receiver'
        r['person'] = r['message'].to

    rendered = render_to_string('message/read.html', r)
    return HttpResponse(rendered)

@warara.wrap_error
def delete(request):
    server = warara_middleware.get_server()
    sess, _ = warara.check_logged_in(request)
    ret, msg = 1, 1
    del_msg_no = int(request.GET.get('del_msg_no', 0))
    if request.POST.get('message_list_type', 0) == 'inbox':
        flag_inbox = 1
    elif request.GET.get('message_list_type', 0) == 'inbox':
        flag_inbox = 1
        del_msg_no = int(del_msg_no)
    else:
        flag_inbox = 0

    if del_msg_no:
        if flag_inbox:
            msg = server.messaging_manager.delete_received_message(sess, del_msg_no)
        else:
            msg = server.messaging_manager.delete_sent_message(sess, del_msg_no)
    elif request.method == "POST":
        flag_del_enm = request.POST.get('flag_del_enm', 0) #flag_delete_entire_message
        flag_del_enm = int(flag_del_enm)
        for x in range(21): #need_modify
            del_msg_no = request.POST.get('ch_del_%s' % x, 0)
            if del_msg_no:
                del_msg_no = int(del_msg_no)
                if flag_inbox:
                    msg = server.messaging_manager.delete_received_message(sess, int(del_msg_no));
                else:
                    msg = server.messaging_manager.delete_sent_message(sess, int(del_msg_no));
                flag_del_enm=0

        if flag_del_enm and request.POST.get('ch_del_enm', 0):
            del_msg_list = request.POST.get('message_no_strlist', '').split('|')
            for del_msg_no in del_msg_list:
                if del_msg_no:
                    del_msg_no = int(del_msg_no)
                    if flag_inbox:
                        msg = server.messaging_manager.delete_received_message(sess, int(del_msg_no))
                    else:
                        msg = server.messaging_manager.delete_received_message(sess, int(del_msg_no))
                

    return HttpResponseRedirect("/message/%s/?page_no=%s" %
            (request.POST.get('message_list_type', 'inbox'),
                request.POST.get('page_no', 1)))
