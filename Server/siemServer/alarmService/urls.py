from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
    path('allAlarms', views.getAlarmLogs),
	path('getAlarm', views.getAlarm),
	path('editAlarmRules',views.editAlarmRules),
	path('submitAlarmEdit',views.submitAlarmEdit),
	path('alarmMonitoring',views.alarmMonitoring),
	path('alarmSeen',views.alarmSeen),
	path('alarmRules', views.getAlarmRules,name='alarmRules'),
	url(r'^generateAlarm', views.generateAlarm, name = "generateAlarm"),
]