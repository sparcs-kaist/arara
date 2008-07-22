from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^add$', 'warara.blacklist.views.add'),
    (r'^$', 'warara.blacklist.views.index'),
)
