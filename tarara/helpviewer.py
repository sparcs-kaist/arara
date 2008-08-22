#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
import widget

class HelpDialog(urwid.WidgetWrap):
    """
    Creates a BoxWidget that displays a help message
    Attributes:
    b_pressed -- Contains the label of the last button pressed or None if no
                 button has been pressed.
    """
    
    b_pressed = None

    _blank = urwid.Text("")
    _mode = None

    def __init__(self, topic, attr, width, height, body, ):
        """
        topic -- Help topic
        attr -- a tuple (background, button, active_button) of attributes
        width -- width of the message widget
        height -- height of the message widget
        body -- widget displayed beneath the message widget
        """

        #Text widget containing the help:
        basedir = os.path.dirname(__file__)
        help = os.path.join(basedir+"/help", topic + '.txt')
        f = open(help, 'r')
        content = f.read().decode('utf-8')
        f.close()
        msg_widget = urwid.Padding(urwid.Text(content), 'center', width - 4)

        #GridFlow widget containing all the buttons:
        button_widgets = []

        for button in ['OK']:
            button_widgets.append(urwid.AttrWrap(urwid.Button(button, self._action), attr[1], attr[2]))

        button_grid = urwid.GridFlow(button_widgets, 12, 2, 1, 'center')

        #Combine message widget and button widget:
        widget_list = [msg_widget, self._blank, button_grid]
        self._combined = urwid.AttrWrap(widget.Border(urwid.Filler(urwid.Pile(widget_list, 2))), attr[0])
        
        #Place the dialog widget on top of body:
        overlay = urwid.Overlay(self._combined, body, 'center', width, 'middle', height)
        self.quit = False
       
        urwid.WidgetWrap.__init__(self, overlay)

    def _action(self, button):
        """
        Function called when a button is pressed.
        Should not be called manually.
        """
        
        self.b_pressed = button.get_label()
        self.quit = True

# vim: set et ts=8 sw=4 sts=4:
