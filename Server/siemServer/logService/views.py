from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required,login_required

from datetime import datetime, timedelta
import re
import time
import math
import threading
import json
from django.db.models import Sum
from .models import Log,Machine
from alarmService.models import Report, AlarmLog
from logService.models import PredefinedReport
from siemServer.settings import GENERATING_REPORT_TIME

# Create your views here.
@csrf_exempt
def log(request):
	#whitelist ip
	body = json.loads(request.body)
	ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
	#get machine
	machine = Machine.objects.get(ip = ip_address)
	counter = int(body['counter'])
	response = HttpResponse()
	if (machine==None):
		response.status_code = 404
		return response
	#counter check
	if (machine.counter!=counter):
		response.status_code = 404
		return response
	machine.counter = machine.counter + 1
	machine.save()
	facilityList = body['facility']
	severityList = body['severity']
	versionList = body['version']
	timestampList = body['timestamp']
	hostnameList = body['hostname']
	appnameList = body['appname']
	procidList = body['procid']
	msgidList = body['msgid']
	structuredDataList = body['structuredData']
	msgList = body['msg']
	try:
		for i in range(0,len(facilityList)):
			if(timestampList[i]!='NILVALUE'):
				timestampList[i] = datetime.strptime(timestampList[i],'%Y-%m-%dT%H:%M:%S.%f%z')
			else:
				timestampList[i] = None
			logs = Log.objects.create(facility=facilityList[i],severity=severityList[i],version=versionList[i],
			timestamp=timestampList[i],hostname=hostnameList[i],appname=appnameList[i],procid=procidList[i],msgid=msgidList[i],
			structuredData=structuredDataList[i],msg=msgList[i],machine=machine)
		logs.save()
		response.status_code = 200
		return response
	except:
		response.status_code = 400
		return response

@login_required(login_url="/accounts/login")#Za bolje objasnjenje pogledati https://docs.djangoproject.com/en/dev/topics/auth/default/#the-login-required-decorator
@permission_required('logService.get_log')#NazivAplikacije.imePermisije; default permisije koje postoje su: add_nazivModela,change_nazivModela,delete_nazivModela
def getLogs(request):
	try:
		#pages
		fromlog = int(request.GET.get('from') or "0")
		tolog = int(request.GET.get('to') or "50")
		#regex
		facility = request.GET.get('facility') or ""
		severity = request.GET.get('severity') or ""
		hostname = request.GET.get('hostname') or ""
		appname = request.GET.get('appname') or ""
		msgid = request.GET.get('msgid') or ""
		#time
		timestampF = request.GET.get('timestampfrom') or "None"
		timestampT = request.GET.get('timestampto') or "None"

		#filter by caps insensitive regex
		logs = Log.objects.filter(facility__iregex=facility,severity__iregex=severity,hostname__iregex=hostname, appname__iregex=appname, msgid__iregex=msgid)
		if(timestampF!='None'):
			timestampF = datetime.strptime(timestampF,'%Y-%m-%dT%H:%M:%S.%f%z')
		else:
			timestampF = datetime.now() - timedelta(days=5)
		if(timestampT!='None'):
			timestampT = datetime.strptime(timestampT,'%Y-%m-%dT%H:%M:%S.%f%z')
		else:
			timestampT = datetime.now()

		logs = logs.filter(timestamp__range=(timestampF,timestampT))
		#Nesto za paginaciju
		currPage = tolog/50
		logs_len=math.ceil(len(logs)/50)
		total_pages=[]
		for i in range(0,logs_len):
			total_pages.append(i+1)

		logs = logs[fromlog:tolog]

		return render(request, 'logService/allLogs.html', {'logs':logs,'currPage':currPage,'total_pages':total_pages,'fromlog':fromlog,'tolog':tolog,'facility':facility,'severity':severity,'hostname':hostname,'appname':appname,'msgid':msgid})
	except ValueError:
		print("ERROR")
		#Timestamp format was bad
		return render(request, 'logService/allLogs.html', {'logs':[]})

@login_required(login_url="/accounts/login")
#@permission_required('logService.get_report')
def report(request):
	date= datetime.now()
	try:
		if request.GET:
			print('aaaaaaaa')
			selectedMac= request.GET.getlist('cb1') or ""
			selectedA= request.GET.getlist('cb2') or ""
			timestampF = request.GET.get('timestampfrom') or "None"
			timestampT = request.GET.get('timestampto') or "None"
			nForMach = 0
			tForApps = 0
			allParams=[]
			allParams.append(selectedMac)
			allParams.append(selectedA)
			allParams.append([timestampF+" - "+timestampT])
			if (timestampF != 'None'):
				timestampF = datetime.strptime(timestampF, '%Y-%m-%dT%H:%M:%S.%f%z')
			else:
				timestampF = datetime.now() - timedelta(days=5)
			if (timestampT != 'None'):
				timestampT = datetime.strptime(timestampT, '%Y-%m-%dT%H:%M:%S.%f%z')
			else:
				timestampT = datetime.now()

			logs = Log.objects.filter(timestamp__range=(timestampF, timestampT))
			for m in selectedMac:
				for t in selectedA:
					print(t)
					print(m)
					if logs.filter(machine__ip=m, appname=t) != "None":
						nForMach += len(logs.filter(machine__ip=m, appname=t))
			print("juhuuu")
			print(nForMach)
			alarms = AlarmLog.objects.filter(time__range=(timestampF, timestampT))
			numbOfAlarms = len(alarms)
			emAlarms = len(alarms.filter(alarm__type='0'))
			alAlarms = len(alarms.filter(alarm__type='1'))
			crtAlarms = len(alarms.filter(alarm__type='2'))
			errAlarms = len(alarms.filter(alarm__type='3'))
			warAlarms = len(alarms.filter(alarm__type='4'))
			ntcAlarms = len(alarms.filter(alarm__type='5'))
			predefined= PredefinedReport.objects.create(time= datetime.now(), generatedFor=allParams,
														numbOfAllLogs= nForMach, numbOfAllAlarms= numbOfAlarms,
														nOfEmergAlarms= emAlarms, nOfAlertAlarms= alAlarms,
														nOfCritAlarms= crtAlarms, nOfErrAlarms= errAlarms,
														nOfWarnAlarms= warAlarms, nOfNotcAlarms= ntcAlarms)
			predefined.save()

		machines= Machine.objects.all()
		apps= Log.objects.order_by().values('appname').distinct()
		reports= Report.objects.all()
		total=reports.aggregate(Sum('numbOfAllLogs'), Sum('numbOfAllAlarms'), Sum('numbOfWinLogs'), Sum('numbOfLinLogs'), Sum('numbOfWinAlarms'), Sum('numbOfLinAlarms'))
	except ValueError:
		print("ERROR")
	return render(request, 'logService/report.html', {'reports': reports, 'machines': machines, 'apps': apps, 'total': total})

@login_required(login_url="/accounts/login")
#@permission_required('logService.get_report')
def predefineReports(request):
	try:
		predefined= PredefinedReport.objects.all()
	except ValueError:
		print("ERROR")
	return render(request, 'logService/predefined.html', {'predefined': predefined})

def reportGenerate():
	print("Sss")
	time= datetime.now()
	try:
		lastR= [Report.objects.order_by('-id')[0]]
	except:
		lastR= None
	print(lastR)
	print("Sss")
	logs = Log.objects.all()
	alarms = AlarmLog.objects.all()
	print(len(alarms.filter(logs__machine__system = 'W')))
	winLogs= len(logs.filter(machine__system= 'W'))
	lnxLogs = len(logs.filter(machine__system = 'L'))
	winAlarms = len(alarms.filter(logs__machine__system = 'W'))
	lnxAlarms = len(alarms.filter(logs__machine__system = 'L'))
	report = Report.objects.create(timestamp=datetime.now(), numbOfAllLogs=len(logs), numbOfAllAlarms=len(alarms), numbOfWinLogs=winLogs,
								numbOfLinLogs=lnxLogs, numbOfWinAlarms=winAlarms, numbOfLinAlarms=lnxAlarms)
	report.save()

def reportGeneratorRunner():
	t1 = threading.Thread(target=reportGeneratorBeat)
	t1.start()

def reportGeneratorBeat():
	while(reportGenerating):
		reportGenerate()
		GENERATING_REPORT_TIME=43200
		time.sleep(GENERATING_REPORT_TIME)

reportGenerating = True