from django.conf.urls import url, include
from rest_framework.documentation import include_docs_urls

from . import views


urlpatterns = [

    url(r'^$', views.restEntryPoint.as_view(), name = 'restEntryPoint'),
    url(r'^users/$', views.adminRest.as_view(), name = 'adminRest'),
    url(r'^users/(?P<usr>\w+)/$', views.usersRest.as_view(), name='usersRest'),
#     url(r'rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')), 
    url(r'^outlet/$', views.outletsRest.as_view(), name='outletsRest'),
    url(r'^outlet/(?P<position>[0-9]+)/$', views.outletRest.as_view(), name = 'outletRest'),
    url(r'^schema/', include_docs_urls(title='Users and outlets', schema_url="/pdu/")), 
    url(r'^remtoken/$', views.logOutView.as_view(), name = 'logOutView'),
    url(r'^gettoken/$', views.getToken.as_view(), name = 'getToken'),

]