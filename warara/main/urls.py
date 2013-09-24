from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.main.views.main'),
    (r'^help/$', 'warara.main.views.help'),
    (r'^noti/$', 'warara.main.views.noti'),
    (r'^userinfo/$', 'warara.main.views.get_user_info'),
)
