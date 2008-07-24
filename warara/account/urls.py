from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^register/$','warara.account.views.register'),    
    (r'^login/$','warara.account.views.login'),    
    (r'^logout/$','warara.account.views.logout'),
    (r'^$','warara.account.views.account'),
    (r'^account_modify/$','warara.account.views.account_modify'),
    (r'^password_modify/$','warara.account.views.password_modify'),
)
