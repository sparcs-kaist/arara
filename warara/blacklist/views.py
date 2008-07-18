from django.template.loader import render_to_string
from django.http import HttpResponse

#import arara

def blacklist(request):
    rendered = render_to_string('blacklist/blacklist_frame.html')
    return HttpResponse(rendered)
