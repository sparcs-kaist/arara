from django.conf.urls.defaults import *

urlpatterns = patterns('warara.collection.views',
    (r'^$', 'list'),
    (r'^rss/$', 'rss'),
    (r'^([\d]+)/$', 'read'),
    (r'^([\d]+)/reply/$', 'reply'),
    (r'^([\d]+)/(\d+)/vote/$', 'vote'),
    (r'^([\d]+)/(\d+)/delete/$', 'delete'),
    (r'^search/$', 'search'),
    (r'^([\d]+)/(\d+)/file/(\d+)/$', 'file_download'),
)
