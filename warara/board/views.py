# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.http import HttpResponse


def index(request):
    rendered = render_to_string('board/index.html', {})
    return HttpResponse(rendered)


def list(request, board_name):
    rendered = render_to_string('board/list.html', {})
    return HttpResponse(rendered)
