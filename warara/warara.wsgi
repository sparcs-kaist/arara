#-*- coding: utf-8 -*-
# WSGI Script for Warara Web Frontend
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WARARA_PATH  = os.path.join(PROJECT_PATH, 'gen-py')
THRIFT_PATH  = os.path.join(PROJECT_PATH, 'warara')
sys.path.append(PROJECT_PATH)
sys.path.append(WARARA_PATH)
sys.path.append(THRIFT_PATH)

os.environ['DJANGO_SETTINGS_MODULE'] = 'warara.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
