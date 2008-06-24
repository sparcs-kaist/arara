from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^warara/', include('warara.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
    (r'^$', 'warara.views.index'),
)
