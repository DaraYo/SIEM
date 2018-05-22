from django.db import models

from logService.models import Machine

# Create your models here.
class Alarm(models.Model):
	regfacility = models.CharField(max_length=100)
	regseverity = models.CharField(max_length=100)
	reghostname = models.CharField(max_length=100)
	regappname = models.CharField(max_length=100)
	regmsgid = models.CharField(max_length=100)
	
	text= models.CharField(max_length=1000)
	Emergency='0'
	Alert='1'
	Critical='2'
	Error='3'
	Warning='4'
	Notice='5'
	Type_CHOICES = (
		(Emergency, 'Emergency'),
		(Alert, 'Alert'),
		(Critical, 'Critical'),
		(Error, 'Error'),
		(Warning, 'Warning'),
		(Notice, 'Notice')
		)
	repeat = models.SmallIntegerField()
	type= models.CharField(max_length=1,choices = Type_CHOICES)
	sysspec = models.BooleanField()
	machinespec = models.BooleanField()
	timed = models.BooleanField()
	hours = models.SmallIntegerField(null=True)
	active = models.BooleanField()

	def __str__(self):
		return self.text

	class Meta:
		permissions = (("get_alarm_rules","Can see rules of active alarms"),)
	#default permisije: add_alarm,change_alarm,delete_alarm 

class AlarmLog(models.Model):
    alarm = models.ForeignKey(Alarm,on_delete=models.CASCADE)
    time = models.DateTimeField()
    machine = models.ForeignKey(Machine,null=True, on_delete=False)
    seen = models.BooleanField()
    class Meta:
        permissions = (("get_alarms","Can see active alarms"),)
        #default permisije: add_alarmlog,change_alarmlog,delete_alarmlog 

class Report(models.Model):
    timestamp = models.DateTimeField(null=False)
    numbOfSysLogs= models.SmallIntegerField()
    numbOfMachLogs = models.SmallIntegerField()
    numbOfSysAlarms = models.SmallIntegerField()
    numbOfMachAlarms = models.SmallIntegerField()
    class Meta:
        permissions = (("get_report","Can see report"),)
        #default permisije: add_report,change_report,delete_report 