from django.shortcuts import render
from .models import AlarmLog
# Create your views here.

def getAlarmLogs(request):
	alarms= AlarmLog.objects.all()
	context= {'alarms': alarms}
	return render(request, 'alarmService/allAlarms.html', context)