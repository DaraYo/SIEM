import glob
import requests
import re
import time
import sys
def main():
	#Citanje konfig fajla
	f=open("config.config","r")
	config = f.readlines()
	f.close()
	
	centralAgent=config[0]
	timer=config[1]
	filter=config[2]
	
	
	counter= config[3]
	log_list=[]
	#Izbacivanje osnovnih configa iz liste da bi ostale samo liste direktorijuma
	config.remove(counter)
	config.remove(centralAgent)
	config.remove(timer)
	config.remove(filter)
	counter=eval(counter)
	if(filter=="\n"):
		filter=""
	#Dict koji ce imati podatke o tome od koje linije da cita logove
	messages_dict={}
	#Regex filter
	r = re.compile(filter)

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
	print(len(messages_dict))
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
		for ldl in config:
			log_list=glob.glob(ldl+"/*.log")
			for log in log_list:
				log_file=open(log,"r")
				log_messages=log_file.readlines()
				log_file.close()
				#Provera da li ima nesto novo u fajlu
				if messages_dict[log]<len(log_messages):
					for i in range(messages_dict[log],len(log_messages)):
						#Ovo treba prepraviti da radi sa regex
						print("OVDE2")
						print(log_messages[i])
						
						if r.match(log_messages[i]):	
							print("OVDE")
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
			requests.post(centralAgent,data=payload)
			counter+=1
			

		
if __name__=="__main__":
    main()
