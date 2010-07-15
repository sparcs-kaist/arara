from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.all.views.list'),
    (r'^/$', 'warara.all.views.list'),
    (r'^([\d]+)/$', 'warara.all.views.read'),
    (r'^([\d]+)/reply/$', 'warara.all.views.reply'),
    (r'^([\d]+)/(\d+)/vote/$', 'warara.all.views.vote'),
    (r'^([\d]+)/(\d+)/delete/$', 'warara.all.views.delete'),
    (r'^search/$', 'warara.all.views.search'),
    (r'^delete_file/$', 'warara.all.views.file_delete'),
    (r'^([\d]+)/(\d+)/file/(\d+)/$', 'warara.all.views.file_download'),
)
