from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.board.views.index'),
    (r'^(?P<board_name>[\w\[\]]+)/$', 'warara.board.views.list'),
    (r'^(?P<board_name>[\w\[\]]+)/write/$', 'warara.board.views.write'),
    (r'^([\w\[\]]+)/([\d]+)/$', 'warara.board.views.read'),
    (r'^([\w\[\]]+)/([\d]+)/reply/$', 'warara.board.views.reply'),
    (r'^([\w\[\]]+)/([\d]+)/(\d+)/vote/$', 'warara.board.views.vote'),
    (r'^([\w\[\]]+)/([\d]+)/(\d+)/delete/$', 'warara.board.views.delete'),
)
