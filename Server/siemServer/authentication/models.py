from django.db import models

class Attempts(models.Model):
	uname = models.CharField(max_length=150, null=True)
	lastAttempt = models.DateTimeField(null=True)
	blockDate= models.DateTimeField(null=True)
	counter= models.SmallIntegerField(default=0)
