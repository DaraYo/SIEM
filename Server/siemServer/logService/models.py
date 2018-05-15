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
	facility = models.SmallIntegerField()
	severity = models.SmallIntegerField()
	version = models.SmallIntegerField()
	timestamp = models.DateTimeField(null=True)
	hostname = models.CharField(max_length=50)
	appname = models.CharField(max_length=50)
	procid = models.CharField(max_length=50)
	msgid = models.CharField(max_length=50)
	structuredData = models.TextField()
	msg = models.TextField()
	machine = models.ForeignKey(Machine)
	class Meta:
		ordering = ["-timestamp","-severity"]
		get_latest_by = ["-timestamp"]
		permissions = (("get_log","Can see list of logs"),)
		#default permisije: add_log,change_log,delete_log 
		indexes = [
            models.Index(fields=['-timestamp', 'msgid']),
			models.Index(fields=['-timestamp', 'hostname'], name='timestamp_host_idx'),
			models.Index(fields=['-timestamp', 'appname'], name='timestamp_app_idx'),
            models.Index(fields=['-timestamp'], name='timestamp_idx'),
        ]

	