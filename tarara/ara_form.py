#!/usr/bin/python
# coding: utf-8

import xmlrpclib
import os, sys
import urwid

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(PROJECT_PATH)

import arara
from configuration import *

class ara_form(urwid.Widget):
    def __init__(self, parent, session_key = None):
        self.keymap = {}
        #self.server = arara.get_server()
	self.server = xmlrpclib.Server("http://%s:%s" % (XMLRPC_HOST, XMLRPC_PORT), use_datetime = True)
        self.set_session_key(session_key)
        self.parent = parent
        self.overlay = None
        self.__initwidgets__()

    def set_session_key(self, session_key):
        self.session_key = session_key

    def get_session_key(self):
        return session_key
    
    def update_session(self):
        if self.session_key != None:
            retvalue = self.server.update_session(self.session_key)
        return retvalue[0]

    def get_cursor_coords(self, size):
        return self.mainpile.get_cursor_coords(size)

    def get_pref_col(self, size):
        return self.mainpile.get_pref_col(size)

    def mouse_event(self, size, event, button, col, row, focus):
        return False

    def move_cursor_to_coords(self, size, col, row):
        return self.mainpile.move_cursor_to_coords(size, col, row)

    def render(self, size, focus):
        return self.mainpile.render(size, focus)

    def selectable(self):
        return True

# vim: set et ts=8 sw=4 sts=4:
