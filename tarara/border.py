#!/usr/bin/python
# coding: utf-8

import urwid
class Border(urwid.WidgetWrap):
	def __init__(self, w):
		utf8decode = urwid.escape.utf8decode
		# Define the border characters
		tline = bline = urwid.Divider(utf8decode('─'))
		lline = rline = urwid.SolidFill(utf8decode('│'))
		tlcorner = urwid.Text(utf8decode('┌'))
		trcorner = urwid.Text(utf8decode('┐'))
		blcorner = urwid.Text(utf8decode('└'))
		brcorner = urwid.Text(utf8decode('┘'))
		#trcorner = blcorner = brcorner = tlcorner

		top = urwid.Columns([ ('fixed', 1, tlcorner),
		tline, ('fixed', 1, trcorner) ])
		middle = urwid.Columns( [('fixed', 1, lline),
		w, ('fixed', 1, rline)], box_columns = [0,2],
		focus_column = 1)
		bottom = urwid.Columns([ ('fixed', 1, blcorner),
		bline, ('fixed', 1, brcorner) ])
		pile = urwid.Pile([('flow',top),middle,('flow',bottom)],
		focus_item = 1)
		urwid.WidgetWrap.__init__(self, pile)

