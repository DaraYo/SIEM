from django.db import models

from logService.models import Machine

# Create your models here.
class Alarm(models.Model):
    regexp = models.CharField(max_length=100)
    text= models.CharField(max_length=1000)
    type= models.CharField(max_length=20)
    repeat = models.SmallIntegerField()
    sysspec = models.BooleanField()
    machinespec = models.BooleanField()
    timed = models.BooleanField()
    hours = models.SmallIntegerField(null=True)
    active = models.BooleanField()

    def __str__(self):
        return self.text

class AlarmLog(models.Model):
    alarm = models.ForeignKey(Alarm,on_delete=models.CASCADE)
    time = models.DateTimeField()
    machine = models.ForeignKey(Machine,null=True, on_delete=False)
    seen = models.BooleanField()

class Report(models.Model):
    timestamp = models.DateTimeField(null=False)
    numbOfSysLogs= models.SmallIntegerField()
    numbOfMachLogs = models.SmallIntegerField()
    numbOfSysAlarms = models.SmallIntegerField()
    numbOfMachAlarms = models.SmallIntegerField()