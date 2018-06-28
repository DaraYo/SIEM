from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required,login_required

from django.contrib.auth import authenticate, login

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
from reportlab.pdfgen import canvas

from datetime import datetime, timedelta
import re
import time as tm
from time import sleep,strftime,localtime, gmtime
import math
import threading
import json
from django.db.models import Sum
from django.utils import timezone

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
	allParams = []
	response = HttpResponse(content_type='application/pdf')
	try:
		if request.GET:
			selectedMac= request.GET.getlist('cb1') or ""
			selectedA= request.GET.getlist('cb2') or ""
			timestampF = request.GET.get('timestampfrom') or "None"
			timestampT = request.GET.get('timestampto') or "None"
			nForMach = 0
			tForApps = 0
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
			winCB= request.GET.get('win') or ""
			linCB = request.GET.get('lin') or ""
			if winCB!="" and linCB=="":
				logs= logs.filter(machine__system='W')
			if winCB=="" and linCB!="":
				logs= logs.filter(machine__system='L')
			for m in selectedMac:
				for t in selectedA:
					if logs.filter(machine__ip=m, appname=t) != "None":
						nForMach += len(logs.filter(machine__ip=m, appname=t))
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
			#predefined.save()
			#response = HttpResponse(content_type='application/pdf')
			#response['Content-Disposition'] = 'inline; filename="'+datetime.now()+'.pdf"'
			buffer = BytesIO()
			time= datetime.now()
			p = canvas.Canvas("predefined/"+str(time.date())+"-"+str(time.time().hour)+"."+str(time.time().minute)+ "." + str(time.time().second)+"_predefined.pdf")
			p.drawCentredString(80, 800, 'Izvestaj za '+str(time.date())+' '+str(time.time()))
			p.drawString(80, 740, 'Odabrane masine:')
			i= 740
			if len(selectedMac)==0:
				i-=20
				p.drawString(300, i, '/')
			else:
				for n in selectedMac:
					i-=20
					p.drawString(120, i, str(n))
			i-=40
			p.drawString(80, i, 'Odabrane aplikacije:')
			if len(selectedA) == 0:
				i -= 20
				p.drawString(300, i, '/')
			else:
				for l in selectedA:
					i -= 20
					p.drawString(120, i, str(l))

			i-=40
			p.drawString(80, i, 'Za operativni sistem:')
			i -= 20
			p.drawString(80, i, 'Za period '+ str(timestampF)+" - "+str(timestampT))
			i-= 20
			p.drawString(100, i, 'Ukupan broj logova: '+ str(nForMach))
			i -= 20
			p.drawString(100, i, 'Ukupan broj alarma: '+ str(numbOfAlarms))
			i -= 20
			p.drawString(100, i, 'Broj emergency alarma: '+ str(emAlarms))
			i -= 20
			p.drawString(100, i, 'Broj alert alarma: '+ str(alAlarms))
			i -= 20
			p.drawString(100, i, 'Broj critical alarma: '+ str(crtAlarms))
			i -= 20
			p.drawString(100, i, 'Broj error alarma: '+ str(errAlarms))
			i -= 20
			p.drawString(100, i, 'Broj warning alarma: '+ str(warAlarms))
			i -= 20
			p.drawString(100, i, 'Broj notice alarma: '+ str(ntcAlarms))
			#p.showPage()
			p.save()
			#pdf = buffer.getvalue()
			buffer.close()
			#response.write(pdf)

		machines= Machine.objects.all()
		apps= Log.objects.order_by().values('appname').distinct()
		reports= Report.objects.all()
		total=reports.aggregate(Sum('numbOfAllLogs'), Sum('numbOfAllAlarms'), Sum('numbOfWinLogs'), Sum('numbOfLinLogs'), Sum('numbOfWinAlarms'), Sum('numbOfLinAlarms'))
	except ValueError:
		print("ERROR")
	return render(request, 'logService/report.html', {'reports': reports, 'machines': machines, 'apps': apps, 'total': total, 'allParams': allParams})

@login_required(login_url="/accounts/login")
#@permission_required('logService.get_report')
def predefineReports(request):
	try:
		predefined= PredefinedReport.objects.all()
		print(len(predefined))
	except ValueError:
		print("ERROR")
	return render(request, 'logService/predefined.html', {'preports': predefined})

def reportGenerate():
	timet= timezone.now()
	try:
		lst= Report.objects.last()
		plus= lst.timestamp+ timedelta(hours= 12)
		if(plus> timet):
			timed=plus- timet
			seconds= timed.total_seconds()
			tm.sleep(seconds)
	except:
		lst= None
	logs = Log.objects.all()
	alarms = AlarmLog.objects.all()
	winLogs= len(logs.filter(machine__system= 'W'))
	lnxLogs = len(logs.filter(machine__system = 'L'))
	winAlarms = len(alarms.filter(logs__machine__system = 'W'))
	lnxAlarms = len(alarms.filter(logs__machine__system = 'L'))

	buffer = BytesIO()
	time = datetime.now()
	p = canvas.Canvas("regular/"+str(time.date()) + "-" + str(time.time().hour) + "." + str(time.time().minute)+ "." + str(time.time().second) + ".pdf")

	p.drawString(80, 800, 'Izvestaj za ' + str(time.date()) + ' ' + str(time.time()))
	p.drawString(80, 760, 'Ukupan broj logova: ' + str(logs))
	p.drawString(80, 740, 'Ukupan broj alarma: ' + str(alarms))
	p.drawString(100, 720, 'Broj logova za Windows OS: ' + str(winLogs))
	p.drawString(100, 700, 'Broj logova za Linux OS: ' + str(lnxLogs))
	p.drawString(100, 680, 'Broj alarma za Windows OS: ' + str(winAlarms))
	p.drawString(100,660, 'Broj alarma za Linux OS: ' + str(lnxAlarms))
	p.save()
	buffer.close()
	report = Report.objects.create(timestamp=timezone.now(), numbOfAllLogs=len(logs), numbOfAllAlarms=len(alarms), numbOfWinLogs=winLogs,
								numbOfLinLogs=lnxLogs, numbOfWinAlarms=winAlarms, numbOfLinAlarms=lnxAlarms)
	report.save()

def reportGeneratorRunner():
	t1 = threading.Thread(target=reportGeneratorBeat)
	t1.start()

def reportGeneratorBeat():
	while(reportGenerating):
		reportGenerate()
		GENERATING_REPORT_TIME=43200
		tm.sleep(GENERATING_REPORT_TIME)

reportGenerating = True