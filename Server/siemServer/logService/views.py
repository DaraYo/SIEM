from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from datetime import datetime

from .models import Log

# Create your views here.
@csrf_exempt
def log(request):
	#add protections first
	#REMOTE_ADDR in list of adress
	response = HttpResponse()
	facility = int(request.POST.get('facility'))
	severity = int(request.POST.get('severity'))
	version = int(request.POST.get('version'))
	timestamp = request.POST.get('timestamp')

	if(timestamp!='NILVALUE'):
		timestamp = datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%S.%f%z')
	else:
		timestamp = None
	hostname = request.POST.get('hostname')
	appname = request.POST.get('appname')
	procid = request.POST.get('procid')
	msgid = request.POST.get('msgid')
	structuredData = request.POST.get('structuredData')
	msg = request.POST.get('msg')
	try:
		logs = Log.objects.create(facility=facility,severity=severity,version=version,
		timestamp=timestamp,hostname=hostname,appname=appname,procid=procid,msgid=msgid,
		structuredData=structuredData,msg=msg)
		logs.save()
		response.status_code = 200
		return response
	except:
		response.status_code = 400
		return response
	
	
