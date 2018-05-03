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
			logs = Log.objects.create(facility=int(facilityList[i]),severity=int(severityList[i]),version=int(versionList[i]),
			timestamp=timestampList[i],hostname=hostnameList[i],appname=appnameList[i],procid=procidList[i],msgid=msgidList[i],
			structuredData=structuredDataList[i],msg=msgList[i])
		logs.save()
		response.status_code = 200
		return response
	except:
		response.status_code = 400
		return response
	
	
