from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
    path('allAlarms', views.getAlarmLogs),
	path('getAlarm', views.getAlarm),
	path('alarmRules', views.getAlarmRules,name='alarmRules'),
	url(r'^generateAlarm', views.generateAlarm, name = "generateAlarm"),
]