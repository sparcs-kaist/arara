from django.template.loader import render_to_string
from django.http import HttpResponse

import arara

def test_login():
    server = arara.get_server()
    ret, sess = server.login_manager.login('jacob', 'jacob', '127.0.0.1')
    assert ret == True
    return sess

def get_various_info(request):
    server = arara.get_server()
    sess = test.login()
    r['num_blacklist_member'] = 0
    return r

def add(request):
    if request.method == 'POST':
        blacklist_id = request.POST['blacklist_id']
        server = arara.get_server()
        sess = test_login()
        ret, message = server.blacklist_manager.add(sess, blacklist_id)
        return HttpResponse(message)
    else:
        return HttpResponse('Must use POST')

def index(request):
    rendered = render_to_string('blacklist/index.html')
    return HttpResponse(rendered)
