import codecs
import os
import sys
import traceback
import time
from random import randint
from datetime import datetime


# ----------------------------------------------------------------------
def generateAllEvents(server, logtypes, basePath):
    """
    """
    min=0
    max=60
    if not server:
        serverName = "localhost"
    else:
        serverName = server
    loop_value= True
    while loop_value:
        logtype= logtypes[randint(0, len(logtypes)-1)]
        path = os.path.join(basePath, "%s_%s_log.log" % (serverName, logtype))
        generateEventLogs(serverName, logtype, path)
        time.sleep(randint(min,max))
# ----------------------------------------------------------------------

def generateEventLogs(server, logtype, logPath):
    messages=[
        "An account was logged off.", #1
        "An account was successfully logged on.", #1
        "Special privileges assigned to new logon.",#1
        "A user account was changed.", #1
        "A user's local group membership was enumerated.", #1
        "A security-enabled local group membership was enumerated.", #1
        "An attempt was made to query the existence of a blank password for an account.", #1
        "A logon was attempted using explicit credentials.", #1
        "Cryptographic operation.", #1
        "Key migration operation.", #1
        "Key file operation.", #1
        "The system has returned from a low power state."  # 2 information type
        "A service was installed in the system.", #3 information
        "-",
        "Installation successful.",  # 4 information
        "Started downloading an update."  # 4 information
    ]

    apps=[
        "Microsoft-Windows-WindowsUpdateClient",#4
        "Microsoft-Windows-Security-Auditing", #1
        "Microsoft-Windows-Power-Troubleshooter", #2
        "Service Control Manager" #3
    ]


    numb_of_logs= randint(0,15)
    print ("Logging %s events" % logtype)
    log = codecs.open(logPath, encoding='utf-8', mode='a')

    facility = randint(0, 23)
    severity = randint(0,7)
    pri= (facility*8)+ severity

    the_time= str(datetime.now())
    numbOfMess= randint(0, len(messages)-1)
    if(numbOfMess<=10):
        source=apps[1]
    if(numbOfMess==11):
        source=apps[2]
    if(numbOfMess==12):
        source=apps[3]
    if(numbOfMess==13):
        source= apps[randint(0, len(apps))]
    if(numbOfMess>13):
        source= apps[0]
    msg= messages[numbOfMess]
    counter= randint(0,100)
    log.write("<%s>1 %s %s %s - ID%s - %s\n" % (pri, the_time, server, source, counter, msg))
    log.close()

    print
    "Log creation finished. Location of log is %s" % logPath

if __name__ == "__main__":
    server = None  # None = local machine
    #logTypes = ["System", "Application", "Security"]#, "Setup", "Forwarded"]
    logTypes= ["First", "Second", "Third"]
    generateAllEvents(server, logTypes, "C:")