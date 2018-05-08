from django.shortcuts import render
from .models import AlarmLog,Alarm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
# Create your views here.

def getAlarmLogs(request):
	alarms= AlarmLog.objects.all()
	context= {'alarms': alarms}
	return render(request, 'alarmService/allAlarms.html', context)
