from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.sysop.views.index'),
    (r'^add_board/$', 'warara.sysop.views.add_board'),
    (r'^modify_board/$', 'warara.sysop.views.modify_board'),
    (r'^confirm_user/$', 'warara.sysop.views.confirm_user'),
)
