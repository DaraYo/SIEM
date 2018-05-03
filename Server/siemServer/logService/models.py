from django.db import models

# Create your models here.
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

class Machine(models.Model):
	WINDOWS = 'W'
	LINUX = 'L'
	OS_CHOICES = (
		(WINDOWS, 'Windows'),
		(LINUX, 'Linux')
	)
	ip = models.CharField(max_length=45)
	system = models.CharField(max_length=1, choices = OS_CHOICES)
	counter = models.BigIntegerField()
	