from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.mobile.board.views.index'),
#    (r'^move_article/$','warara.mobile.board.views.move_article'),
    (r'^(?P<board_name>[\w \[\]\.]+)/$', 'warara.mobile.board.views.list'),
#    (r'^(?P<board_name>[\w \[\]\.]+)/write/$', 'warara.mobile.board.views.write'),
    (r'^([\w \[\]\.]+)/([\d]+)/$', 'warara.mobile.board.views.read'),
#    (r'^([\w \[\]\.]+)/([\d]+)/0/$','warara.mobile.board.views.read_root'),
#    (r'^([\w \[\]\.]+)/([\d]+)/reply/$', 'warara.mobile.board.views.reply'),
#    (r'^([\w \[\]\.]+)/([\d]+)/(\d+)/vote/(\+|\-)$', 'warara.mobile.board.views.vote'),
#    (r'^([\w \[\]\.]+)/([\d]+)/(\d+)/delete/$', 'warara.mobile.board.views.delete'),
#    (r'^([\w \[\]\.]+)/([\d]+)/(\d+)/destroy/$', 'warara.mobile.board.views.destroy'),
#    (r'^([\w \[\]\.]+)/search/$', 'warara.mobile.board.views.search'),
#    (r'^([\w \[\]\.]+)/delete_file/$', 'warara.mobile.board.views.file_delete'),
#    (r'^([\w \[\]\.]+)/([\d]+)/(\d+)/file/(\d+)/$', 'warara.mobile.board.views.file_download'),
)
