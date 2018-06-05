from django.db import models

# Create your models here.
class Machine(models.Model):
	WINDOWS = 'W'
	LINUX = 'L'
	OS_CHOICES = (
		(WINDOWS, 'Windows'),
		(LINUX, 'Linux')
	)
	ip = models.CharField(max_length=45, unique=True)
	system = models.CharField(max_length=1, choices = OS_CHOICES)
	counter = models.BigIntegerField(default=0)
	#default permisije: add_machine,change_machine,delete_machine 

class Log(models.Model):
	facility = models.CharField(max_length=2)
	severity = models.CharField(max_length=1)
	version = models.CharField(max_length=5)
	timestamp = models.DateTimeField(null=True)
	hostname = models.CharField(max_length=50)
	appname = models.CharField(max_length=50)
	procid = models.CharField(max_length=50)
	msgid = models.CharField(max_length=50)
	structuredData = models.TextField()
	msg = models.TextField()
	machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
	class Meta:
		ordering = ["-timestamp","-severity", "appname"]
		get_latest_by = ["-timestamp"]
		permissions = (("get_log","Can see list of logs"),)
		#default permisije: add_log,change_log,delete_log 
		indexes = [
            models.Index(fields=['-timestamp', 'msgid']),
			models.Index(fields=['-timestamp', 'hostname'], name='timestamp_host_idx'),
			models.Index(fields=['-timestamp', 'appname'], name='timestamp_app_idx'),
            models.Index(fields=['-timestamp'], name='timestamp_idx'),
        ]

class PredefinedReport(models.Model):
	time = models.DateTimeField(null=False)
	generatedFor= models.CharField(max_length=1000)
	numbOfAllLogs = models.BigIntegerField(default=0)
	numbOfAllAlarms = models.BigIntegerField(default=0)
	nOfEmergAlarms = models.BigIntegerField(default=0)
	nOfAlertAlarms = models.BigIntegerField(default=0)
	nOfCritAlarms = models.BigIntegerField(default=0)
	nOfErrAlarms = models.BigIntegerField(default=0)
	nOfWarnAlarms = models.BigIntegerField(default=0)
	nOfNotcAlarms = models.BigIntegerField(default=0)
