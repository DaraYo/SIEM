from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from datetime import datetime

from .models import Log
#from alarmService.models import AlarmLog

# Create your views here.
@csrf_exempt
def log(request):
	#add protections first
	#REMOTE_ADDR in list of adress
    #alarms= AlarmLog.objects.all()
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
		logs = Log.objects.all()
		context = {'logs': logs}
		#response.status_code = 400
		return render(request, 'logService/allLogs.html', context)#response

def getLogs(request):
	logs= Log.objects.all()
	context= {'logs': logs}
	if(request.GET.get('search')):
		value= request.GET.get('version').strip()
		value2 = request.GET.get('msgId').strip()
		value3 = request.GET.get('msg').strip()
		logs= Log.objects.filter(version__contains=value, msgid__contains=value2, msg__contains=value3)
		print('drugi put cao')
	return render(request, 'logService/allLogs.html', context)
