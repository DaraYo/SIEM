import asyncio
import json
import websockets
import threading
import logging
import pathlib
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError

from alarmService.views import alarmCheckRunner, getAlarmingLogs
from logService.views import reportGeneratorRunner

#prep for web sockets
USERS = set()

async def notify_alarm_logs():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = getAlarmingLogs()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)
    await notify_alarm_logs()

async def unregister(websocket):
    USERS.remove(websocket)

async def alarmSocket(websocket, path):
    await register(websocket)
    print("New user at web socket(user count:"+ str(len(USERS)) +" )")
    try:
        await websocket.send(getAlarmingLogs())
        async for message in websocket:#keeps it connected
            pass
    finally:
        await unregister(websocket)
        print("User left web socket(user count:"+ str(len(USERS)) +" )")


#startup
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
    #start web socket
    t1 = threading.Thread(target=webSocketThread)
    t1.start()
    #run other threads
    alarmCheckRunner()
    reportGeneratorRunner()

def webSocketThread():
    asyncio.set_event_loop(asyncio.new_event_loop())
    #secure version
    import ssl
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #ssl_context.load_cert_chain(pathlib.Path(__file__).with_name('certificate.pem'))
    ssl_context.load_cert_chain('siemServer/certificate.pem','siemServer/privateKey.pem')
    asyncio.get_event_loop().run_until_complete(websockets.serve(alarmSocket, 'localhost', 6789, ssl=ssl_context))
    asyncio.get_event_loop().run_forever()
    '''
    asyncio.get_event_loop().run_until_complete(websockets.serve(alarmSocket, 'localhost', 6789))
    asyncio.get_event_loop().run_forever()
    '''
