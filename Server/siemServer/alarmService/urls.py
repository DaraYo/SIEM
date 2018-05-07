from django.urls import path
from . import views

urlpatterns = [
    path('allAlarms', views.getAlarmLogs),
]