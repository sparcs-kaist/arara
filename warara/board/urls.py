from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.board.views.index'),
    (r'^(?P<board_name>[\w\[\]]+)/$', 'warara.board.views.list'),
    (r'^(?P<board_name>[a-zA-Z0-9]+)/write/$', 'warara.board.views.write'),
    (r'^(?P<board_name>[a-zA-Z0-9]+)/write_/$', 'warara.board.views.write_'),
)
