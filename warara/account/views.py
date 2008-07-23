from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

#import arara

def index(request):
    rendered = render_to_string('account/index.html')
    return HttpResponse(rendered)
