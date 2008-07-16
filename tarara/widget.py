#!/usr/bin/python
# coding: utf-8

import urwid

class Selectable:
    def selectable(self):
        return True
    def keypress(self, size, key):
        return key

class Item(Selectable, urwid.AttrWrap):
    def __init__(self, text, attr, focus_attr=None):
        w = urwid.Text(text)
        urwid.AttrWrap.__init__(self, w, attr, focus_attr)

class MarkedItem(Selectable, urwid.WidgetWrap):
    def __init__(self, marker, widget):
        width = len(marker)
        self.focus = ('fixed', width, urwid.Text(marker))
        self.blur = ('fixed', width, urwid.Text(' ' * width))
        self.w = widget
    def render(self, size, focus=False):
        if focus:
            marker = self.focus
        else:
            marker = self.blur
        widget = urwid.Columns([marker, self.w])
        return widget.render(size, focus)

class FieldRow(urwid.WidgetWrap):
    def __init__(self, data):
        self.w = self.make_widget(data)
    def make_widget(self, data):
        widgets = []
        for field in self.fields:
            key, width, align = field
            value = data[key]
            widget = urwid.Text(value, align, 'clip')
            if not width:
                widgets.append(widget)
            else:
                widgets.append(('fixed', width, widget))
        return urwid.Columns(widgets, dividechars=1)

# vim: set et ts=8 sw=4 sts=4:

