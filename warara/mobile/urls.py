from django.conf.urls.defaults import *

urlpatterns = patterns('',
#    (r'^$', 'warara.mobile.main.urls'), # TODO : Link this to the main page of mobile (maybe login..?)
    (r'^account/', include('warara.mobile.account.urls')),
    (r'^board/', include('warara.mobile.board.urls')),
    (r'^main/', include('warara.mobile.main.urls')),

#    (r'^blacklist/', include('warara.mobile.blacklist.urls')),
#    (r'^message/', include('warara.mobile.message.urls')),
#    (r'^all/', include('warara.mobile.all.urls')),
#    (r'^sysop/', include('warara.mobile.sysop.urls')),
)
