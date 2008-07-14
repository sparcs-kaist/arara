import urwid

class Selectable:
    def selectable(self):
        return True
    def keypress(self, size, key):
        return key

class MarkerSelect(Selectable, urwid.WidgetWrap):
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
