from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^login/$','warara.mobile.account.views.login'),
    (r'^logout/$','warara.mobile.account.views.logout'),
)
