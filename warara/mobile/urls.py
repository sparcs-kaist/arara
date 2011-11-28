from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.mobile.main.views.index'),
    (r'^account/', include('warara.mobile.account.urls')),
    (r'^board/', include('warara.mobile.board.urls')),
    (r'^main/', include('warara.mobile.main.urls')),
    (r'^all/', include('warara.mobile.all.urls')),

#    (r'^blacklist/', include('warara.mobile.blacklist.urls')),
#    (r'^message/', include('warara.mobile.message.urls')),
#    (r'^sysop/', include('warara.mobile.sysop.urls')),
)
