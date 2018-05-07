from django.shortcuts import render
from .models import AlarmLog
# Create your views here.

def getAlarms(request):
    alarms= AlarmLog.objects.all()