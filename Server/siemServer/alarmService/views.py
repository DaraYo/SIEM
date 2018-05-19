from django.shortcuts import render
from .models import AlarmLog,Alarm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url="/login")
def getAlarmLogs(request):
	alarms= AlarmLog.objects.all()
	context= {'alarms': alarms}
	return render(request, 'alarmService/allAlarms.html', context)
@csrf_exempt
def generateAlarm(request):
	a = Alarm()
	a.regexp = request.POST.get('regexp')
	a.text = request.POST.get('text')
	a.type = request.POST.get('type')
	a.repeat = request.POST.get('repeat')
	if(request.POST.get('sysspec')=='on'):
		a.sysspec = True
	else:
		a.sysspec = False
	if request.POST.get('macspec')=='on':
		a.machinespec = True
	else:
		a.machinespec = False
	if request.POST.get('timed')=='on':
		a.timed = True
		a.hours = request.POST.get('hours')
	else:
		a.timed = False
		a.hours = 0
	a.active = True
	
	a.save()
	#response.status_code = 200
	return redirect('alarmRules')

def getAlarmRules(request):
	alarmRules = Alarm.objects.all()
	context = {'alarmrules':alarmRules}
	return render(request, 'alarmService/alarmRules.html',context)

def createRule(request):
	return render(request,'alarmService/createRule.html')
