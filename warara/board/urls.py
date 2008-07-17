from django.conf.urls.defaults import *

urlpatterns = patterns('',
    ('^$', 'warara.board.views.index'),
    ('^(?P<board_name>[a-z]+)/$', 'warara.board.views.list'),
)
