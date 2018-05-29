from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('log', views.log),
    url(r'^getLogs', views.getLogs),
    path('report', views.report)
	
]