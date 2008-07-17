# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse

import arara

def test_login():
    server = arara.get_server()
    ret, sess = server.login_manager.login('breadfish', 'breadfish', '127.0.0.1')
    assert ret == True
    return sess

def get_various_info():
    server = arara.get_server()
    sess = test_login()
    r = {}  # render_item
    r['num_new_message'] = 0
    r['num_message'] = 0
    r['m_list_key'] = [{'internal':'sorr', 'th':''},
            {'internal':'message', 'th':'text'},
            {'internal':'sent_time', 'th':'time'}]
    ret, r['m_list'] = server.messaging_manager.receive_list(sess)

    return r


def inbox(request):
    r = get_various_info()
    r['m_list_key'][r['m_list_key'].index({'internal':'sorr', 'th':''})] = {'internal':'from', 'th':'sender'}
    r['message_list_type'] = 'inbox'

    rendered = render_to_string('message/message_list.html', r)
    return HttpResponse(rendered)

def outbox(request):
    r = get_various_info()
    r['message_list_type'] = 'outbox'
    
    rendered = render_to_string('message/message_list.html', r)
    return HttpResponse(rendered)
