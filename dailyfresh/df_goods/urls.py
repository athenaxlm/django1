from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index),
    url('^(\d+)$', views.detail),
    url('^list(\d+)$', views.good_list),
    url(r'^search/$', views.MySearchView.as_view()),
]
