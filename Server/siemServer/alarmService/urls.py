from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
    path('allAlarms', views.getAlarmLogs),
	path('alarmRules', views.getAlarmRules,name='alarmRules'),
	path('createRule',views.createRule,name='createRule'),
	url(r'^generateAlarm', views.generateAlarm, name = "generateAlarm"),
]