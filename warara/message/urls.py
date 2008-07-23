from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^inbox/$', 'warara.message.views.inbox'),
    (r'^(inbox)/(\d+)/$', 'warara.message.views.read'),
    (r'^outbox/$', 'warara.message.views.outbox'),
    (r'^(outbox)/(\d+)/$', 'warara.message.views.read'),
    (r'^send/$', 'warara.message.views.send'),
    (r'^delete/(\d+)/$', 'warara.message.views.delete'),
    (r'^reply/(\d+)/$', 'warara.message.views.send'),
)
