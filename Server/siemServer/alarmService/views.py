import time
import threading
import json
import asyncio
import websockets
import pytz
from datetime import datetime,timedelta
from collections import Counter
import math
from django.shortcuts import render
from .models import AlarmLog,Alarm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required

from logService.models import Log
import siemServer

# Create your views here.

@login_required(login_url="/accounts/login")
@permission_required('alarmService.get_alarms')
def getAlarmLogs(request):
	#pages
	fromalarm = int(request.GET.get('from') or "0")
	toalarm = int(request.GET.get('to') or "50")
	
	#time
	timestampF = request.GET.get('timestampfrom') or "None"
	timestampT = request.GET.get('timestampto') or "None"
	
	alarms= AlarmLog.objects.all()
	
	if(timestampF!='None'):
		timestampF = datetime.strptime(timestampF,'%Y-%m-%dT%H:%M:%S.%f%z')
	else:
		timestampF = datetime.now(pytz.utc) - timedelta(days=5)
	if(timestampT!='None'):
		timestampT = datetime.strptime(timestampT,'%Y-%m-%dT%H:%M:%S.%f%z')
	else:
		timestampT = datetime.now(pytz.utc)
		
	alarms = alarms.filter(time__range=(timestampF,timestampT))
	
	
	currPage = toalarm/50
	alarms_len=math.ceil(len(alarms)/50)
	total_pages=[]
	for i in range(0,alarms_len):
		total_pages.append(i+1)

	alarms = alarms[fromalarm:toalarm]
	context= {'alarms': alarms,'currPage':currPage,'total_pages':total_pages,'fromalarm':fromalarm,'toalarm':toalarm}
	return render(request, 'alarmService/allAlarms.html', context)

@login_required(login_url="/accounts/login")
@permission_required('alarmService.add_alarm')
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
		if(request.POST.get('repeat')==''):
			a.repeat=1
		else:
			a.repeat = request.POST.get('repeat')
		if(request.POST.get('sysspec')=='on'):
			a.sysspec = True
		else:
			a.sysspec = False
		if request.POST.get('macspec')=='on':
			a.machinespec = True
		else:
			a.machinespec = False
		if(request.POST.get('appspec')=='on'):
			a.appspec = True
		else:
			a.appspec = False
		if(request.POST.get('rmispec')=='on'):
			a.rmispec = True
		else:
			a.rmispec = False
		if request.POST.get('hours')=='':
			a.minutes = 0
		else:
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

@login_required(login_url="/accounts/login")
@permission_required('alarmService.get_alarm_rules')
def getAlarm(request):
	response = HttpResponse()
	try:
		alarmZ = AlarmLog.objects.get(pk=request.GET.get('id'))
		context = {'a':alarmZ}
		return render(request,'alarmService/alarm.html',context)
	except:
		response.status_code = 406
		return response
	
@login_required(login_url="/accounts/login")
@permission_required('alarmService.change_alarm')
def alarmSeen(request):
	response = HttpResponse()
	try:
		alarmZ = AlarmLog.objects.get(pk=request.GET.get('id'))
		alarmZ.seen= True
		alarmZ.save()
		t1 = threading.Thread(target=notifyChange)
		t1.start()
		context = {'a':alarmZ}
		return render(request,'alarmService/alarm.html',context)
	except:
		response.status_code = 406
		return response

@login_required(login_url="/accounts/login")
@permission_required('alarmService.change_alarm')
def editAlarmRules(request):
	response = HttpResponse()
	try:
		alarm=Alarm.objects.get(pk=request.GET.get('id'))
		context={'alarm':alarm}
		return render(request,'alarmService/editAlarmRules.html',context)
	except:
		response.status_code = 406
		return response

@login_required(login_url="/accounts/login")
@permission_required('alarmService.get_alarms')
def alarmMonitoring(request):
	return render(request,'alarmService/alarmMonitoring.html')

@login_required(login_url="/accounts/login")
@permission_required('alarmService.change_alarm')
@csrf_exempt
def submitAlarmEdit(request):
	response = HttpResponse()
	try:
		a=Alarm.objects.get(pk=request.POST.get('id'))
		a.regfacility = request.POST.get('regfacility')
		a.regseverity = request.POST.get('regseverity')
		a.reghostname = request.POST.get('reghostname')
		a.regappname = request.POST.get('regappname')
		a.regmsgid = request.POST.get('regmsgid')
		a.text = request.POST.get('text')
		a.type = request.POST.get('type')
		if(request.POST.get('repeat')==''):
			a.repeat=1
		else:
			a.repeat = request.POST.get('repeat')
		if(request.POST.get('sysspec')=='on'):
			a.sysspec = True
		else:
			a.sysspec = False
		if request.POST.get('macspec')=='on':
			a.machinespec = True
		else:
			a.machinespec = False
		if(request.POST.get('appspec')=='on'):
			a.appspec = True
		else:
			a.appspec = False
		if(request.POST.get('rmispec')=='on'):
			a.rmispec = True
		else:
			a.rmispec = False
		if request.POST.get('hours')=='':
			a.minutes = 0
		else:
			a.minutes = eval(request.POST.get('hours'))
		if( request.POST.get('active')=='on'):
			a.active=True
		else:
			a.active=False
		
		a.save()
		#response.status_code = 200
		return redirect('alarmRules')
	except:
		response.status_code = 406
		return response
	
#Alarm checker area
def getAlarmingLogs():
	alarms= AlarmLog.objects.filter(seen=False)
	listOfLogs = []
	for alarmlog in alarms:
		textOfAlarm = alarmlog.alarm.text
		typeOfAlarm = alarmlog.alarm.type
		timeOfAlarm = (alarmlog.time).strftime('%d.%m.%Y. %H:%M:%S.%f %z')
		idOfLog = alarmlog.id
		logObject = {"type":typeOfAlarm,"text":textOfAlarm,"time":timeOfAlarm,"id":idOfLog}
		listOfLogs.append(logObject)
	return json.dumps(listOfLogs)
		
#NEW ALARMING#
def repAlarm(alarmRule, logs, timestampF, timestampT, type, *rest):
	#print('-------->REP ALARM HERE')
	counter = Counter()
	changed = False
	if type=='us':
		#print('--------->counting system')
		for log in logs:
			counter[log.machine.system] += 1
	elif type=='um':
		#print('--------->counting machine')
		for log in logs:
			counter[log.machine.id] += 1
	elif type=='ua':
		#print('--------->counting appname')
		for log in logs:
			counter[log.appname] += 1
	else:#'ui'
		#print('--------->counting msgid')
		for log in logs:
			counter[log.msgid] += 1
	
	for celement in counter.items():
		#print('---------->element:'+str(celement[0])+' repeats:'+str(celement[1]))
		if celement[1]>=alarmRule.repeat:
			#get alarmlog if it exists
			existingAlarmLog = AlarmLog.objects.filter(alarm__id=alarmRule.id,time__range=(timestampF,timestampT),seen=False)
			if len(existingAlarmLog)>0:
				existingAlarmLog = existingAlarmLog[0]
			else:
				existingAlarmLog = None
			#print('----------->unique checks left:'+str(len(list(rest))))
			if len(list(rest))<1:
				#old alarm
				if existingAlarmLog!=None:
					#print('------------->>Updating alarm')
					existingLogs = existingAlarmLog.logs.all()
					if type=='us':
						for log in logs:
							if log.machine.system == celement[0] and log not in existingLogs:
								existingAlarmLog.logs.add(log)
								changed = True
					elif type=='um':
						for log in logs:
							if log.machine.id == celement[0] and log not in existingLogs:
								existingAlarmLog.logs.add(log)
								changed = True
					elif type=='ua':
						for log in logs:
							if log.appname == celement[0] and log not in existingLogs:
								existingAlarmLog.logs.add(log)
								changed = True
					else:#'ui'
						for log in logs:
							if log.msgid == celement[0] and log not in existingLogs:
								existingAlarmLog.logs.add(log)
								changed = True
				#new alarm
				else:
					#print('------------->>New alarm')
					alarmlog = AlarmLog.objects.create(alarm=alarmRule,time=datetime.now(pytz.utc),seen=False)
					alarmlog.save()
					changed = True
					if type=='us':
						for log in logs:
							if log.machine.system == celement[0]:
								alarmlog.logs.add(log)
					elif type=='um':
						for log in logs:
							if log.machine.id == celement[0]:
								alarmlog.logs.add(log)
					elif type=='ua':
						for log in logs:
							if log.appname == celement[0]:
								alarmlog.logs.add(log)
					else:#'ui'
						for log in logs:
							if log.msgid == celement[0]:
								alarmlog.logs.add(log)
			else:
				#print('-------------->Preping logs for restart')
				tmplogs = []
				if type=='us':
					for log in logs:
						if log.machine.system == celement[0]:
							tmplogs.append(log)
				elif type=='um':
					for log in logs:
						if log.machine.id == celement[0]:
							tmplogs.append(log)
				elif type=='ua':
					for log in logs:
						if log.appname == celement[0]:
							tmplogs.append(log)
				else:#'ui'
					for log in logs:
						if log.msgid == celement[0]:
							tmplogs.append(log)
				#print("------------> Refire with logs:"+str(len(tmplogs)))
				changed = changed or repAlarm(alarmRule,tmplogs,timestampF,timestampT,*rest)
				#print("------------> changed after refire:"+str(changed))
	#print("----------> Changed at the end:"+str(changed))
	return changed

def alarmCheck():
	#print("++++++++++ALARM CHECK+++++++++")
	changed = False
	counter = Counter()
	alarmRules = Alarm.objects.filter(active=True)
	for alarmRule in alarmRules:
		#print("==============> NEXT ALARM")###
		counter.clear()
		facility = alarmRule.regfacility
		severity = alarmRule.regseverity
		hostname = alarmRule.reghostname
		appname = alarmRule.regappname
		msgid = alarmRule.regmsgid
		timestampT = datetime.now(pytz.utc)
		timestampF = datetime.now(pytz.utc) - timedelta(minutes=alarmRule.minutes)
		#logovi se ne pribavljaju iz baze dok nisu potrebni, tako da je kod ispod koji se sastoji od vise filtriranja ekvivalentan 1 pozivanju iz baze
		logs = Log.objects.filter(facility__iregex=facility,severity__iregex=severity,hostname__iregex=hostname, appname__iregex=appname, msgid__iregex=msgid)
		logs = logs.filter(timestamp__range=(timestampF,timestampT))
		#print("====>len(LOGS):"+str(len(logs)))
		checklist=[]
		if alarmRule.machinespec:
			checklist.append('um')
		if alarmRule.sysspec:
			checklist.append('us')
		if alarmRule.rmispec:
			checklist.append('ui')
		if alarmRule.appspec:
			checklist.append('ua')
		#print("====> checklist size:"+str(len(checklist)))###
		if(len(checklist)>=1):
			#print("====> calling check for size:"+str(len(checklist)))###
			changed = repAlarm(alarmRule,logs,timestampF,timestampT,*checklist) or changed
			#print("====> CHANGED at this point:"+str(changed))###
		else:#no uniqe
			#print("====> checking for no uniqes")###
			if logs.count()>=alarmRule.repeat:
				existingAlarmLog = AlarmLog.objects.filter(alarm__id=alarmRule.id,time__range=(timestampF,timestampT),seen=False)
				if len(existingAlarmLog)>0:
					existingAlarmLog = existingAlarmLog[0]
				else:
					existingAlarmLog = None
				if existingAlarmLog!=None:
					#print("++++> updating alarm")###
					existingLogs = existingAlarmLog.logs.all()
					for log in logs:
						if log not in existingLogs:
							existingAlarmLog.logs.add(log)
							changed = True
				else:
					#print("++++> creating alarm")###
					alarmlog = AlarmLog.objects.create(alarm=alarmRule,time=datetime.now(pytz.utc),seen=False)
					alarmlog.save()
					changed = True
					for log in logs:
						alarmlog.logs.add(log)
			#print("====> CHANGED at this point:"+str(changed))###
	if changed:
		t1 = threading.Thread(target=notifyChange)
		t1.start()
	
def alarmCheckRunner():
	t1 = threading.Thread(target=alarmCheckBeat)
	t1.start()

def alarmCheckBeat():
	while(alarmBeatRunning):
		time.sleep(siemServer.settings.CHECK_EVERY_X_SECONDS)
		alarmCheck()
	
async def change():
	async with websockets.connect('ws://localhost:6789') as websocket:
		await websocket.recv()

def notifyChange():
	asyncio.set_event_loop(asyncio.new_event_loop())
	asyncio.get_event_loop().run_until_complete(change())

alarmBeatRunning = True
