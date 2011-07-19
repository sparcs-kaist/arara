from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^logout/$','warara.mobile.account.views.logout'),
)
