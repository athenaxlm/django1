from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^register/$', views.RegisterView.as_view(),name='register'),
    url(r'^username$',views.username),
    url(r'^send_active_mail$',views.send_active_mail),
    url(r'^active/(.+)',views.user_active),
    url(r'^login$',views.loginView.as_view()),
    url(r'^logout$',views.logout_view),
    url('^$',views.info),
    url('^order$',views.order),
    url('^site$',views.SiteView.as_view()),
    url('^area$',views.area)


]