from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

#import arara

def register(request):
    rendered = render_to_string('account/register.html')
    return HttpResponse(rendered)
