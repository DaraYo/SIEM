import glob
import requests
import re
import time
import sys
from ruamel import yaml
from settings import centralAgent,timer,filter,directoriums
def main():

	
	f=open("config.config","r")
	config = f.readlines()
	f.close()
	counter= eval(config[0])
	
	config=directoriums
	#Dict koji ce imati podatke o tome od koje linije da cita logove
	messages_dict={}
	#Regex filter
	r = re.compile(filter)
	log_list=[]
	#Formiranje dicta
	for ldl in config:
		log_list=glob.glob(ldl+"/*.log")
		for log in log_list:
			log_file=open(log,"r")
			log_messages=log_file.readlines()
			log_file.close()
			#fname=log.split('\\')
			#messages_dict[fname[len(fname)-1]]=len(log_messages)
			messages_dict[log]=len(log_messages)

	while True:
		facility_l=[]
		severity_l=[]
		version_l=[]
		timestamp_l=[]
		hostname_l=[]
		appname_l=[]
		procid_l=[]
		msgid_l=[]
		sdata_l=[]
		msg_l=[]
		sys.stdout.flush()
		time.sleep(eval(timer))
		#for ldl in config:
		#	log_list=glob.glob(ldl+"/*.log")
			for log in log_list:
				log_file=open(log,"r")
				log_messages=log_file.readlines()
				log_file.close()
				#Provera da li ima nesto novo u fajlu
				if messages_dict[log]<len(log_messages):
					for i in range(messages_dict[log],len(log_messages)):
						#Ovo treba prepraviti da radi sa regex
						if r.match(log_messages[i]):	
							parts = log_messages[i].split(" ")
							PRIVERS = parts[0].split(">")
							PRI = PRIVERS[0].split("<")[1]
							VERSION=PRIVERS[1]
							FACILITY=eval(PRI)//8
							SEVERITY=eval(PRI)%8
							timestamp = parts[1]
							if(timestamp!='NILVALUE'):
								if timestamp[-1]=='Z':
									timestamp = timestamp[:-1] + '+0000'
								else:
									timestamp = timestamp[:-6] + timestamp[-6:].replace(':','')
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
							facility_l.append(FACILITY)
							severity_l.append(SEVERITY)
							version_l.append(VERSION)
							timestamp_l.append(timestamp)
							hostname_l.append(HOSTNAME)
							appname_l.append(APPNAME)
							procid_l.append(PROCID)
							msgid_l.append(MSGID)
							sdata_l.append(SDATA)
							msg_l.append(MSG)
				messages_dict[log]=len(log_messages)
		#Slanje listi na server
		if len(msg_l)!=0:
			print("Sent "+str(len(msg_l))+" messages to server")
			payload={'counter':counter,'facility':facility_l,'severity':severity_l,'version':version_l,'timestamp':timestamp_l,'hostname':hostname_l,'appname':appname_l,'procid':procid_l,'msgid':msgid_l,'structuredData':sdata_l,'msg':msg_l}
			requests.post(centralAgent,json=payload)
			counter+=1
			f = open("config.config","w")
			print(counter,file=f)
			f.close()
			

		
if __name__=="__main__":
    main()
