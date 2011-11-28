from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.mobile.all.views.list'),
#    (r'^rss/$', 'warara.mobile.all.views.rss'),
    (r'^([\d]+)/$', 'warara.mobile.all.views.read'),
    (r'^([\d]+)/reply/$', 'warara.mobile.all.views.reply'),
    (r'^([\d]+)/(\d+)/vote/$', 'warara.mobile.all.views.vote'),
    (r'^([\d]+)/(\d+)/delete/$', 'warara.mobile.all.views.delete'),
    (r'^search/$', 'warara.mobile.all.views.search'),
#    (r'^delete_file/$', 'warara.mobile.all.views.file_delete'),
    (r'^([\d]+)/(\d+)/file/(\d+)/$', 'warara.mobile.all.views.file_download'),
)
