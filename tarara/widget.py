#!/usr/bin/python
# coding: utf-8

import urwid

utf8decode = urwid.escape.utf8decode
dash = urwid.SolidFill(utf8decode('-'))
blank = urwid.SolidFill(u" ")
blanktext = urwid.Filler(urwid.Text(' '))
nfblanktext = urwid.Text(' ')

class Selectable:
    def selectable(self):
        return True
    def keypress(self, size, key):
        return key

class Item(Selectable, urwid.AttrWrap):
    def __init__(self, text, attr, focus_attr=None):
        w = urwid.Text(text)
        urwid.AttrWrap.__init__(self, w, attr, focus_attr)

class NonTextItem(Selectable, urwid.AttrWrap):
    def __init__(self, w, attr, focus_attr=None):
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
            if type(value) in ['int','bool','date']:
                widget = urwid.Text(str(value), align, 'clip')
            else:
                widget = urwid.Text(value, align, 'clip')
            if not width:
                widgets.append(widget)
            else:
                widgets.append(('fixed', width, widget))
        return urwid.Columns(widgets, dividechars=1)

class Border(urwid.WidgetWrap):
    def __init__(self, w):
        #utf8decode = urwid.escape.utf8decode
        utf8decode = lambda x: x
        # Define the border characters
        tline = bline = urwid.Divider(utf8decode('--'))
        lline = urwid.Filler(urwid.Text(utf8decode('| \n| \n| \n| \n| \n| \n| \n| \n| \n| \n| \n| \n| \n| \n| \n| ')))
        rline = urwid.Filler(urwid.Text(utf8decode(' |\n |\n |\n |\n |\n |\n |\n |\n |\n |\n |\n |\n |\n |\n |\n |')))
        tlcorner = urwid.Text(utf8decode('+-'))
        trcorner = urwid.Text(utf8decode('-+'))
        blcorner = urwid.Text(utf8decode('+-'))
        brcorner = urwid.Text(utf8decode('-+'))

        top = urwid.Columns([ ('fixed', 2, tlcorner), tline, ('fixed', 2, trcorner) ])
        middle = urwid.Columns( [('fixed', 2, lline), w, ('fixed', 2, rline)], box_columns = [0,2], focus_column = 1)
        bottom = urwid.Columns([ ('fixed', 2, blcorner), bline, ('fixed', 2, brcorner) ])
        pile = urwid.Pile([('flow',top),middle,('flow',bottom)], focus_item = 1)
        urwid.WidgetWrap.__init__(self, pile)

class PasswordEdit(urwid.Edit):
    def get_text(self):
        return self.caption + "*"*len(self.edit_text), self.attrib

class Dialog(urwid.WidgetWrap):
    """
    Creates a BoxWidget that displays a message, an edit field (optionally)
    and some buttons on top of another BoxWidget.

    Attributes:

    b_pressed -- Contains the label of the last button pressed or None if no
                 button has been pressed.
    edit_text -- After a button is pressed, this contains the text the user
                 has entered in the edit field
    """
   
    b_pressed = None;
    edit_text = None;

    _blank = urwid.Text("");
    _edit_widget = None;

    def __init__(self, msg, buttons, attr, width, height, body, edit=None,
                 edit_text=""):
        """
        msg -- content of the message widget, one of:
                   plain string -- string is displayed
                   (attr, markup2) -- markup2 is given attribute attr
                   [markupA, markupB, ... ] -- list items joined together
        buttons -- a list of strings with the button labels
        attr -- a tuple (background, button, active_button) of attributes
        height -- height of the message widget
        width -- width of the message widget
        body -- widget displayed beneath the message widget
        edit -- If \"Text\" or \"Int\", a corresponding edit widget will be
                displayed under the message, Otherwise, the edit widget will be
                omitted.
        edit_text -- default value to be edited
        """

        #Text widget containing the message:
        msg_widget = urwid.Padding(urwid.Text(msg), 'center', width - 4);

        #GridFlow widget containing all the buttons:
        button_widgets = [];

        for button in buttons:
            button_widgets.append(urwid.AttrWrap(
                urwid.Button(button, self._action), attr[1], attr[2]));

        button_grid = urwid.GridFlow(button_widgets, 12, 2, 1, 'center');

        #Combine message widget, button widget and (possibly) edit widget:
        if edit == "Text": #with text edit
            self._edit_widget = urwid.Edit("", edit_text);
            edit_pad = urwid.Padding(urwid.AttrWrap(
                self._edit_widget, attr[1], attr[2]), 'center', width - 4);
            widget_list = [msg_widget, self._blank, edit_pad, self._blank,
                           button_grid];
                       
        elif edit == "Int": #with integer edit
            self._edit_widget = urwid.IntEdit("", edit_text);
            edit_pad = urwid.Padding(urwid.AttrWrap(
                self._edit_widget, attr[1], attr[2]), 'center', width - 4);
            widget_list = [msg_widget, self._blank, edit_pad, self._blank,
                           button_grid];
           
        else: #plain message without edit widget:
            widget_list = [msg_widget, self._blank, button_grid];

           
        combined = urwid.AttrWrap(Border(urwid.Filler(urwid.Pile(widget_list, 2))),
                                  attr[0]);

        #Place the dialog widget on top of body:
        overlay = urwid.Overlay(combined, body, 'center', width,
                                'middle', height);
        self.quit = False
       
        urwid.WidgetWrap.__init__(self, overlay);

    def _action(self, button):
        """
        Function called when a button is pressed.
        Should not be called manually.
        """
       
        self.b_pressed = button.get_label();
        if self._edit_widget:
            self.edit_text = self._edit_widget.get_edit_text();
        self.quit = True

def EasyColumn(widget1, widget2,ratio1=60, ratio2=40):
    return urwid.Columns([
        ('weight', ratio1, widget1),
        ('weight', ratio2, widget2),
        ])

def IndentColumn(widget, indent=1):
    return urwid.Columns([('fixed', indent, nfblanktext), widget,])

# vim: set et ts=8 sw=4 sts=4:

