from django.urls import path
from . import views

urlpatterns = [
    path('log', views.log),
    path('allLogs', views.getLogs),
]