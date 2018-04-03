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