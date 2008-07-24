from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^register/$','warara.account.views.register'),    
    (r'^login/$','warara.account.views.login'),    
    (r'^logout/$','warara.account.views.logout'),    
)
