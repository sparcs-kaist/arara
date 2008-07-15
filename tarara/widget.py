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

class RowItem(FieldRow):
    fields = [
        ('number', 5, 'right'),
        ('id', 8, 'left'),
        ('name', 10, 'left'),
        ('date', 5, 'right'),
        ('subject', 0, 'left'),
    ]

class ListView(object):
    def make_widget(data):
        return widget.MarkerSelect('>', RowItem(data))

    def make_header():
        data = {'number': u'번호', 'id': u'글쓴이', 'name': u'이름', 'date': u'날짜', 'subject': u'제목'}
        return urwid.AttrWrap(make_widget(data), 'reversed')

    def get_view():
        walker = urwid.SimpleListWalker([make_widget({'number': '1', 'id': '2', 'name': 'peremen', 'date': 'today', 'subject': 'good article'})])

        body = urwid.ListBox(walker)
        header = make_header()
        return urwid.Frame(body, header)
