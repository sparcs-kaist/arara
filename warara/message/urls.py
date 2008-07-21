from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^inbox/$', 'warara.message.views.inbox'),
    (r'^outbox/$', 'warara.message.views.outbox'),
    (r'^send/$', 'warara.message.views.send'),
    (r'^send_/$', 'warara.message.views.send_'),
)
