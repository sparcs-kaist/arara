from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^mypage', 'warara.blacklist.views.blacklist'),
)
