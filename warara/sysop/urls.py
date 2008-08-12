from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.sysop.views.index'),
    (r'^add_board/$', 'warara.sysop.views.add_board'),
    (r'^remove_board/$', 'warara.sysop.views.remove_board'),
)
