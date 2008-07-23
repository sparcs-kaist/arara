from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^register/$','warara.account.views.register'),    
)
