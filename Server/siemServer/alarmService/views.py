import time
import threading
from datetime import datetime,timedelta
from collections import Counter

from django.shortcuts import render
from .models import AlarmLog,Alarm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required

from logService.models import Log
from siemServer.settings import CHECK_EVERY_X_SECONDS

# Create your views here.

@login_required(login_url="/accounts/login")
@permission_required('alarmService.get_alarms')
def getAlarmLogs(request):
	alarms= AlarmLog.objects.all()
	context= {'alarms': alarms}
	return render(request, 'alarmService/allAlarms.html', context)

@csrf_exempt
def generateAlarm(request):
	a = Alarm()
	response = HttpResponse()
	try:
		a.regfacility = request.POST.get('regfacility')
		a.regseverity = request.POST.get('regseverity')
		a.reghostname = request.POST.get('reghostname')
		a.regappname = request.POST.get('regappname')
		a.regmsgid = request.POST.get('regmsgid')
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
		if request.POST.get('hours')=='':
			a.timed = False
			a.minutes = 0
		else:
			a.timed = True
			a.minutes = eval(request.POST.get('hours'))
		a.active = True
		
		a.save()
		#response.status_code = 200
		return redirect('alarmRules')
	except:
		response.status_code = 406
		return response

@login_required(login_url="/accounts/login")
@permission_required('alarmService.get_alarm_rules')
def getAlarmRules(request):
	alarmRules = Alarm.objects.all()
	context = {'alarmrules':alarmRules}
	return render(request, 'alarmService/alarmRules.html',context)

@login_required(login_url="/accounts/login")
@permission_required('alarmService.add_alarm')
def createRule(request):
	return render(request,'alarmService/createRule.html')

def alarmCheck():
	changed = False
	coutner = Counter()
	alarmRules = Alarm.objects.filter(active=True)
	for alarmRule in alarmRules:
		facility = alarmRule.regfacility
		severity = alarmRule.regseverity
		hostname = alarmRule.reghostname
		appname = alarmRule.regappname
		msgid = alarmRule.regmsgid
		timestampT = datetime.now()
		timestampF = datetime.now() - timedelta(minutes=alarmRule.minutes)
		#logovi se ne pribavljaju iz baze dok nisu potrebni, tako da je kod ispod koji se sastoji od vise filtriranja ekvivalentan 1 pozivanju iz baze
		logs = Log.objects.filter(facility__iregex=facility,severity__iregex=severity,hostname__iregex=hostname, appname__iregex=appname, msgid__iregex=msgid)
		logs = logs.filter(timestamp__range=(timestampF,timestampT))
		if alarmRule.machinespec:
			for log in logs:
				coutner[log.machine.id] += 1#mozda moze samo log.machine ali tesko
			for celement in counter.items():
				if celement[1]>=alarmRule.repeat:
					alarmlog = AlarmLog.objects.create(alarm=alarmRule,time=datetime.now(),seen=False)
					alarmlog.save()
					changed = True
					for log in logs:
						if log.machine.id == celement[0]:
							alarmlog.logs.add(log)
		else:
			if alarmRule.sysspec:
				for log in logs:
					coutner[log.machine.system] += 1#mozda moze samo log.machine ali tesko
				for celement in counter.items():
					if celement[1]>=alarmRule.repeat:
						alarmlog = AlarmLog.objects.create(alarm=alarmRule,time=datetime.now(),seen=False)
						alarmlog.save()
						changed = True
						for log in logs:
							if log.machine.system == celement[0]:
								alarmlog.logs.add(log)
			else:
				if logs.count()>=alarmRule.repeat:
					alarmlog = AlarmLog.objects.create(alarm=alarmRule,time=datetime.now(),seen=False)
					alarmlog.save()
					changed = True
					for log in logs:
						if log.machine.system == celement[0]:
							alarmlog.logs.add(log)
	if changed:
		print("Alarm se desio pokreni event da se obavesti korisnik koji osluskuje")
	
def alarmCheckRunner():
	t1 = threading.Thread(target=alarmCheckBeat)
	t1.start()

def alarmCheckBeat():
	while(alarmBeatRunning):
		time.sleep(CHECK_EVERY_X_SECONDS)
		alarmCheck()

alarmBeatRunning = True