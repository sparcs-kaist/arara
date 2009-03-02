from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^register/$','warara.account.views.register'),    
    (r'^register/agreement/$','warara.account.views.agreement'),
    (r'^register/idcheck/$','warara.account.views.id_check'),
    (r'^register/nicknamecheck/$','warara.account.views.nickname_check'),
    (r'^register/emailcheck/$','warara.account.views.email_check'),
    (r'^login/$','warara.account.views.login'),    
    (r'^logout/$','warara.account.views.logout'),
    (r'^$','warara.account.views.account'),
    (r'^account_modify/$','warara.account.views.account_modify'),
    (r'^password_modify/$','warara.account.views.password_modify'),
    (r'^account_remove/$','warara.account.views.account_remove'),
    (r'^confirm/(\w+)/(\w+)/$','warara.account.views.confirm_user'),
    (r'^reconfirm/(\w+)/$','warara.account.views.reconfirm_user'),
    (r'^register/resendemail/$','warara.account.views.mail_resend'),
)
