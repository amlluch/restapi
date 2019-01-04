
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views


from pdu import views

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^admin/', admin.site.urls),
    url(r'^test$', views.test, name='test'),
    url(r'^prueba$', views.prueba, name='prueba'),
    url(r'^mail$', views.test_mail, name='test_mail'),
    url(r'^rlogin$', views.remotelogin, name='remotelogin'),
    url('restapi/', include('restapi.urls'),),
]
