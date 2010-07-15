import os
import settings
PROJECT_PATH = settings.PROJECT_PATH

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.main.views.index'),
    (r'^account/', include('warara.account.urls')),
    (r'^blacklist/', include('warara.blacklist.urls')),
    (r'^board/', include('warara.board.urls')),
    (r'^message/', include('warara.message.urls')),
    (r'^all/', include('warara.all.urls')),
    (r'^sysop/', include('warara.sysop.urls')),
    (r'^main/', include('warara.main.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(PROJECT_PATH, 'media')}),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url':'/media/image/favicon.ico'}),

)
