from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required,login_required

from datetime import datetime, timedelta
import re
import time
import math
from .models import Log,Machine
from alarmService.models import Report, AlarmLog
from siemServer.settings import GENERATING_REPORT_TIME

# Create your views here.
def log(request):
	#whitelist ip
	ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
	#get machine
	machine = Machine.objects.get(ip = ip_address)
	counter = int(request.POST.get('counter'))
	if (machine==None):
		return
	#counter check
	if (machine.counter!=counter):
		return
	response = HttpResponse()
	machine.counter = machine.counter + 1
	machine.save()
	facilityList = request.POST.get('facility')
	severityList = request.POST.get('severity')
	versionList = request.POST.get('version')
	timestampList = request.POST.get('timestamp')
	hostnameList = request.POST.get('hostname')
	appnameList = request.POST.get('appname')
	procidList = request.POST.get('procid')
	msgidList = request.POST.get('msgid')
	structuredDataList = request.POST.get('structuredData')
	msgList = request.POST.get('msg')
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
		logs_len=math.ceil(len(logs)/50)
		total_pages=[]
		for i in range(0,logs_len):
			total_pages.append(i+1)
		print(total_pages)
		#
		logs = logs[fromlog:tolog]

		return render(request, 'logService/allLogs.html', {'logs':logs,'total_pages':total_pages,'fromlog':fromlog,'tolog':tolog,'facility':facility,'severity':severity,'hostname':hostname,'appname':appname,'msgid':msgid})
	except ValueError:
		print("ERROR")
		#Timestamp format was bad
		return render(request, 'logService/allLogs.html', {'logs':[]})

@login_required(login_url="/accounts/login")
#@permission_required('logService.get_report')
def report(request):
	date= datetime.now()
	try:
		reports=[]
		#reports= Report.objects.all()
		#todaysReport= Report.objects.get(timestamp= date)
		#logs=Log.objects.all()
		#alarms=AlarmLog.objects.all()
		#todaysReport.numbOfAllLogs= len(logs)
		#todaysReport.numbOfAllAlarms= len(alarms)
		#lmachine = request.GET.get('logmach') or ""
		#lsystem = request.GET.get('logsys') or ""
		#amachine = request.GET.get('almach') or ""
		#asystem = request.GET.get('alsys') or ""
		print("he")
	except ValueError:
		print("ERROR")
	return render(request, 'logService/report.html', {'reports': reports})

def reportGenerate():
	logs = Log.objects.all()
	alarms = AlarmLog.objects.all()
	winLogs= logs.filter(machine__system= 'Windows')
	lnxLogs = logs.filter(machine__system = 'Linux')
	winAlarms = alarms.filter(logs__sysspec = True)
	# lnxLogs = alarms.filter(machine__system = 'Linux')
	print("hehe")

def reportGeneratorRunner():
	t1 = threading.Thread(target=reportGeneratorBeat)
	t1.start()

def reportGeneratorBeat():
	while(reportGenerating):
		time.sleep(GENERATING_REPORT_TIME)
		reportGenerate()

reportGenerating = True