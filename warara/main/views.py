from django.template.loader import render_to_string
from django.http import HttpResponse

def index(request):
    rendered = render_to_string('index.html', {})
    return HttpResponse(rendered)
