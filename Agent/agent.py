import glob
import requests
def main():
    CIA = "https://localhost:8000"

    f = open("config.config", "r")
    logs_directorium_list = f.readlines()
    f.close()

    messages_dict={}
    
    for ldl in logs_directorium_list:
        log_list = glob.glob(ldl + "/*.log")
        for log in log_list:
            log_file = open(log, "r")
            log_messages = log_file.readlines()
            log_file.close()
            messages_dict[log]=len(log_messages)
            for message in log_messages:
                parts = message.split(" ")
                PRIVERS = parts[0].split(">")
                PRI = PRIVERS[0].split("<")[1]
                VERSION=PRIVERS[1]
                FACILITY=eval(PRI)//20
                SEVERITY=eval(PRI)%20
                TIMESTAMP = parts[1]
                HOSTNAME = parts[2]
                APPNAME = parts[3]
                PROCID = parts[4]
                MSGID= parts[5]
                SDATAMSG=""
                for i in range(6,len(parts)):
                    SDATAMSG=SDATAMSG+" "+parts[i]
                SDATAMSG=SDATAMSG.strip()
                if(SDATAMSG[0]=='['):
                    SDATA=SDATAMSG.split("]")[0]+"]"
                    MSG=SDATAMSG.split("]")[1]
                else:
                    DATA=SDATAMSG.split(" ")
                    SDATA=DATA[0]
                    MSG=""
                    for i in range(1,len(DATA)):
                       MSG=MSG+" "+DATA[i]
                MSG=MSG.strip()
                payload={'facility':FACILITY,'severity':SEVERITY,'version':VERSION,'timestamp':TIMESTAMP,'hostname':HOSTNAME,'appname':APPNAME,'procid':PROCID,'msgid':MSGID,'structuredData':SDATA,'msg':MSG}
                requests.post(CIA,data=payload)
    print(messages_dict)
    while True:
        for ldl in logs_directorium_list:
            log_list = glob.glob(ldl + "/*.log")
            for log in log_list:
                log_file = open(log, "r")
                log_messages = log_file.readlines()
                log_file.close()
                if(messages_dict[log]<len(log_messages)):
                    messages_dict[log]=len(log_messages)
                    for i in range(messages_dict[log],len(log_messages)):
                        parts = log_messages[i].split(" ")
                        PRIVERS = parts[0].split(">")
                        PRI = PRIVERS[0].split("<")[1]
                        VERSION=PRIVERS[1]
                        FACILITY=eval(PRI)//20
                        SEVERITY=eval(PRI)%20
                        TIMESTAMP = parts[1]
                        HOSTNAME = parts[2]
                        APPNAME = parts[3]
                        PROCID = parts[4]
                        MSGID= parts[5]
                        SDATAMSG=""
                        for i in range(6,len(parts)):
                            SDATAMSG=SDATAMSG+" "+parts[i]
                        SDATAMSG=SDATAMSG.strip()
                        if(SDATAMSG[0]=='['):
                            SDATA=SDATAMSG.split("]")[0]+"]"
                            MSG=SDATAMSG.split("]")[1]
                        else:
                            DATA=SDATAMSG.split(" ")
                            SDATA=DATA[0]
                            MSG=""
                            for i in range(1,len(DATA)):
                               MSG=MSG+" "+DATA[i]
                        MSG=MSG.strip()
                        payload={'facility':FACILITY,'severity':SEVERITY,'version':VERSION,'timestamp':TIMESTAMP,'hostname':HOSTNAME,'appname':APPNAME,'procid':PROCID,'msgid':MSGID,'structuredData':SDATA,'msg':MSG}
                        requests.post(CIA,data=payload)
    
if __name__=="__main__":
    main()

        
