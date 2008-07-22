from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^add/$', 'warara.blacklist.views.add'),
    (r'^update/$', 'warara.blacklist.views.update'),
    (r'^delete/$', 'warara.blacklist.views.delete'),
    (r'^$', 'warara.blacklist.views.index'),
)
