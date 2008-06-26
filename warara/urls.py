from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^warara/', include('warara.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
    (r'^main/$', 'warara.views.main'),
    (r'^list/([^/]+)/$', 'warara.views.list'),
    (r'^modify/([^/]+)/(\d)+/$', 'warara.views.modify'),
    (r'^write/([^/]+)/$', 'warara.views.write'),
    (r'^message/send/$', 'warara.views.write_message'),
    (r'^message/inbox/$', 'warara.views.inbox_list'),
    (r'^message/outbox/$', 'warara.views.outbox_list'),
)
