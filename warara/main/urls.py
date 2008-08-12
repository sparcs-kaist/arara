from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^help/$', 'warara.main.views.help'),
)
