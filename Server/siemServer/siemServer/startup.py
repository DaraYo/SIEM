from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError

from alarmService.views import alarmCheckRunner
from logService.views import reportGeneratorRunner

def start():
    groupO, created = Group.objects.get_or_create(name='operator')
    if (created):
        groupO.permissions.clear()
        permission = Permission.objects.get(codename='get_alarms')
        groupO.permissions.add(permission)
        permission = Permission.objects.get(codename='get_log')
        groupO.permissions.add(permission)
    groupA, created = Group.objects.get_or_create(name='administrator')
    if (created):
        groupA.permissions.clear()
        permission = Permission.objects.get(codename='get_alarms')
        groupA.permissions.add(permission)
        permission = Permission.objects.get(codename='get_log')
        groupA.permissions.add(permission)
        permission = Permission.objects.get(codename='get_alarm_rules')
        groupA.permissions.add(permission)
        permission = Permission.objects.get(codename='add_alarm')
        groupA.permissions.add(permission)
        permission = Permission.objects.get(codename='change_alarm')
        groupA.permissions.add(permission)
        permission = Permission.objects.get(codename='delete_alarm')
        groupA.permissions.add(permission)
        permission = Permission.objects.get(codename='get_report')
        groupA.permissions.add(permission)
    #adding users
    try:
        user = User.objects.create_user("operator1", "someoperatoremail@gmail.com", "o9xp..s15.")
        user.groups.add(groupO)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user("administrator1", "someadministratoremail@gmail.com", "isk45.13.a")
        user.groups.add(groupA)
        user.save()
    except IntegrityError:
        pass
    alarmCheckRunner()
    reportGeneratorRunner()