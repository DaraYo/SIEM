from django.db import models

from logService.models import Machine

# Create your models here.
class Alarm(models.Model):
    regexp = models.CharField(max_length=100)
    repeat = models.SmallIntegerField()
    sysspec = models.BooleanField()
    machinespec = models.BooleanField()
    timed = models.BooleanField()
    hours = models.SmallIntegerField(null=True)
    active = models.BooleanField()

class AlarmLog(models.Model):
    alarm = models.ForeignKey(Alarm,on_delete=models.CASCADE)
    time = models.DateTimeField()
    machine = models.ForeignKey(Machine,null=True)
    seen = models.BooleanField()
