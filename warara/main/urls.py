from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.main.views.main'),
    (r'^help/$', 'warara.main.views.help'),
)
