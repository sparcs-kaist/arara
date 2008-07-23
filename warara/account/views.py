from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

import arara

def register(request):
    if request.method == 'POST':
        username = request.POST['id']
        password = request.POST['password']
        nickname = request.POST['nickname']
        email = request.POST['email']
        signature = request.POST['sig']
        introduction = request.POST['introduce']
        language = request.POST['language']
        user_information_dic = {'username':username, 'password':password, 'nickname':nickname, 'email':email, 'signature':signature, 'self_introduction':introduction, 'default_language':language}
        server = arara.get_server()
        ret, message = server.member_manager.register(user_information_dic)
        assert ret, message
        return HttpResponseRedirect("/")
    else:
        rendered = render_to_string('account/register.html')
        return HttpResponse(rendered)
