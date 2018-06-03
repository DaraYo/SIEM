import random
import socket
import os
from collections import Counter
from time import sleep,strftime,localtime

NOOFUSERS = 10

FREQUENCY = {'min': 10,'max':15}#time in secounds
USERSPEED = {'min': 1,'max':5}#time in secounds

MINFUNCTIONS = 1
MAXFUNCTIONS = 3

DOCCHANCE = Counter(A=170,B=100,C=130,D=120,E=100,F=50,G=25,H=25,I=50,J=100,K=5,L=5,M=5,N=5,O=5,P=5,Q=75,R=25)#1000 total
ADMINCHANCE = Counter(A=10,B=10,C=10,D=10,E=10,F=10,G=10,H=10,I=10,J=10,K=200,L=100,M=100,N=200,O=150,P=150,Q=0,R=0)#1000 total
UNREGCHANCE = Counter(A=10,B=10,C=10,D=10,E=10,F=10,G=10,H=10,I=10,J=10,K=10,L=10,M=10,N=10,O=10,P=10,Q=420,R=420)#1000 total

FAILCHANCE = Counter(Emergency=1,Alert=3,Critical=3,Error=5,Warning=13,Notice=75)
LOGINCHANCE = Counter(S=80,F=20)

DEST_LOGIN = "./Services/authLog.log"

DEST_MAIL = "./Services/mailLog.log"

DEST_WIKI = "./Wiki/log.log"

DEST_APP = "./App/appLog.log"

DEST_DB = "./App/dbLog.log"

DEST_INSTRUMENT = "./Services/machineLog.log"

def getUser():
	return random.choice(['a','d','u'])
	
def getRandom(chanceCounter):
	chanceList = sorted(chanceCounter.elements())
	random.shuffle(chanceList)
	index = random.randint(0,len(chanceList)-1)
	return chanceList[index]

def writeLog(path,facility,severity,msgid,sdata,msg):
	version = 1
	timestamp = localtime()
	timestamp = strftime('%Y-%m-%dT%H:%M:%S.00%z', timestamp)
	hostname = socket.gethostname()
	appname = "app-sim"
	procid = '-'
	
	num = facility*8 + severity
	
	string = "<" + str(num) + ">"+str(version)+" "+ timestamp + " " + hostname + " " + appname + " " + procid + " " + msgid + " " + sdata + " " + msg + "\n"
	
	file = open(path,'a')
	file.write(string)
	file.close()
	
def simulateUserAction():
	userChance = {'a':ADMINCHANCE, 'd':DOCCHANCE, 'u':UNREGCHANCE}
	userType = getUser()
	print("User type: " + userType)
	userChance = userChance[userType]
	if userType=='d':
		start_shift()
	for userFunctionIndex in range(0,random.randint(MINFUNCTIONS-1,MAXFUNCTIONS)):
		print("Action started")
		sleep(random.randint(USERSPEED['min'],USERSPEED['max']))
		FUNCTIONS[getRandom(userChance)](userType)
		print("Action done")
	if userType=='d':
		end_shift()
		
		
def main():
	app = DEST_APP.split("/")[:-1]
	db = DEST_DB.split("/")[:-1]
	inst = DEST_INSTRUMENT.split("/")[:-1]
	log = DEST_LOGIN.split("/")[:-1]
	mail = DEST_MAIL.split("/")[:-1]
	wiki = DEST_WIKI.split("/")[:-1]
	for a in [app,db,inst,log,mail,wiki]:
		path = '/'.join(a)
		try:
			os.mkdir(path)
		except:
			pass
	for i in range(0,NOOFUSERS):
		print("======== User no: "+(str(i+1))+" ==========")
		simulateUserAction()
		sleep(random.randint(FREQUENCY['min'],FREQUENCY['max']))
		
#20 functions
#users docs, admin, unreg

#login
def loginCheck():
	return getRandom(LOGINCHANCE)
	
def login(userType):
	if(userType=='u'):
		return
	while True:
		if loginCheck()=='S':
			writeLog(DEST_DB,23,6,"authenticate","-","Authentication confirmed")
			writeLog(DEST_LOGIN,4,6,"user"+userType,"-","User successfully loged in")
			return
		else:
			writeLog(DEST_DB,23,5,"authenticate","-","Authentication faild")
			writeLog(DEST_LOGIN,4,5,"user"+userType,"-","User faild to log in")

#DOC
def start_shift():
	type = random.choice(['general','surgeon','nurse'])
	type2 = random.choice(['general','surgeon','nurse'])
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_APP,16,4,"-",'[userData@32473 job="'+type2+'"]',"Previous user faild to end job, forcefully ending")
		writeLog(DEST_APP,16,6,"-","-","User ended daily job")
		writeLog(DEST_APP,16,6,type,"-","User started daily job")
	else:
		writeLog(DEST_APP,16,6,type,"-","User started daily job")
	
def end_shift():
	writeLog(DEST_APP,16,6,"-","-","User ended daily job")

def get_patient_data(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to get patient data")
		return
	doc = random.choice(['malcom','andy','maya'])
	writeLog(DEST_DB,23,6,"get","-","Patient data requested")
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_APP,17,1,doc,"-","Patient data not found")
		writeLog(DEST_MAIL,2,5,"new_patient","-","Email sent to admin")
	else:
		writeLog(DEST_APP,17,6,doc,"-","Patient data aquired")
		
def print_info(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	state = getRandom(FAILCHANCE)
	if state!="Notice":
		if state!="Warning":
			writeLog(DEST_APP,17,6,'printer',"-","Print request sent")
			writeLog(DEST_INSTRUMENT,6,1,'printer',"-","Printer stoped working")
			writeLog(DEST_MAIL,2,5,"critical","-","Email sent to admin")
			writeLog(DEST_APP,17,1,'printer',"-","Printer is not working")
		else:
			writeLog(DEST_APP,17,6,'printer',"-","Print request sent")
			writeLog(DEST_INSTRUMENT,6,5,'printer','-',"Print request on wait")
			sleep(2)
			writeLog(DEST_INSTRUMENT,6,6,'printer','-','Data printed')
	else:
		writeLog(DEST_APP,17,6,'printer',"-","Print request sent")
		writeLog(DEST_INSTRUMENT,6,6,'printer','-','Data printed')
		
def set_appointment(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to set appointment")
		return
	doc = random.choice(['malcom','andy','maya'])
	state = getRandom(FAILCHANCE)
	if(state!="Notice"):
		if(state=="Warning"):
			writeLog(DEST_DB,23,6,"insert","-","Created new appointment")
			writeLog(DEST_APP,17,6,doc,"-","New appointment set")
			writeLog(DEST_APP,17,4,doc,"-","Maximal amount of appointments reached for a day")
		else:
			writeLog(DEST_APP,17,3,doc,"-","Maximal amount of appointments already reached, faild to create appointment")
	else:
		writeLog(DEST_DB,23,6,"insert","-","Created new appointment")
		writeLog(DEST_APP,17,6,doc,"-","New appointment set")
		
def give_prescription(userType):
	doc = random.choice(['malcom','andy','maya'])
	state = getRandom(FAILCHANCE)
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	if state!="Notice":
		writeLog(DEST_APP,17,4,doc,"-","Patient is alergin to prescription, aborted by app")
	else:
		writeLog(DEST_DB,23,6,"insert","-","Created new prescription")
		writeLog(DEST_APP,17,6,doc,"-","Prescription given out")
		writeLog(DEST_APP,17,6,'printer',"-","Print prescription request sent")
		writeLog(DEST_INSTRUMENT,6,6,'printer','-','Prescription printed')
	
		
def update_patient_data(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	doc = random.choice(['malcom','andy','maya'])
	writeLog(DEST_DB,23,6,"update","-","Patient data updated")
	writeLog(DEST_APP,17,6,doc,"-","Patient data updated")
	
	
		
def reserve_operation_room(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	doc = random.choice(['malcom','andy','maya'])
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_APP,17,1,doc,"-","Operatioinal rooms full")
	else:
		writeLog(DEST_MAIL,2,5,"reservation","-","Email sent to organiser")
		writeLog(DEST_APP,17,6,doc,"-","Operational room reserved")
		
def alert_area(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_INSTRUMENT,6,1,'alert','-','Alarm bell not working')
	else:
		writeLog(DEST_MAIL,2,1,"alert","-","Email sent to doctors")
		writeLog(DEST_APP,17,1,"alert","-","Area alert trigered")
		writeLog(DEST_INSTRUMENT,6,1,'alert','-','Alarm bell was triggered')
		
def request_transport_for_patient(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	doc = random.choice(['malcom','andy','maya'])
	writeLog(DEST_MAIL,2,5,"transport","-","Email sent requesting transport")
	writeLog(DEST_APP,17,5,doc,"-","Transport request sent")
		
def comunicate(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_MAIL,2,3,"comunication","-","Email faild to be sent, service down")
		writeLog(DEST_MAIL,2,7,"comunication","-","Debug: Mail server error at:...")
	else:
		writeLog(DEST_MAIL,2,6,"comunication","-","Email sent requesting transport")

		
def read_announcements(userType):
	if(userType!='d'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	writeLog(DEST_DB,23,6,"get","-","Announcement data requested")
	writeLog(DEST_APP,17,6,"announcement","-","Announcement checked")

#ADMIN
def add_announcements(userType):
	if(userType!='a'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	writeLog(DEST_DB,23,6,"insert","-","Announcement added")
	writeLog(DEST_APP,17,6,"announcement","-","Announcement added")

def register_doc(userType):
	if(userType!='a'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	writeLog(DEST_DB,23,6,"insert","-","New doctor registerd")
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_DB,23,4,"insert","-","New doctor has same name as existing one")
	writeLog(DEST_APP,17,6,"announcement","-","Announcement added")
		
def remove_doc(userType):
	if(userType!='a'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	writeLog(DEST_DB,23,5,"delete","-","Doctor removed")
	writeLog(DEST_APP,17,6,"delete","-","Doctor removed from users")
	
def set_schedule(userType):
	if(userType!='a'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_APP,17,3,"schedule","-","Schedule already set for this week")
	else:
		writeLog(DEST_APP,17,6,"schedule","-","Schedule set")

		
def edit_wiki(userType):
	if(userType!='a'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_WIKI,22,5,"edit","-","Wiki page edited")
	else:
		writeLog(DEST_DB,23,6,"insert","-","New wiki page created")
		writeLog(DEST_WIKI,22,6,"add","-","Wiki page edited")
		
def add_patient_data(userType):
	if(userType!='a'):
		writeLog(DEST_APP,20,4,"unauthorized",'[invalidData@32473 user="'+userType+'"]',"Unauthorized request to print data")
		return
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_DB,23,3,"insert","-","Error inserting in to database")
	else:
		writeLog(DEST_DB,23,6,"insert","-","New patient data created")
		writeLog(DEST_APP,17,6,"patient","-","New patient data created")
		writeLog(DEST_MAIL,2,6,"comunication","-","Email information sent")

#UNREG
def read_wiki(userType):
	if getRandom(FAILCHANCE)!="Notice":
		writeLog(DEST_DB,23,6,"get","-","Wiki data requested")
		writeLog(DEST_WIKI,22,5,"view","-","Nonexistant page requested")
	else:
		writeLog(DEST_DB,23,6,"get","-","Wiki data requested")
		writeLog(DEST_WIKI,22,6,"view","-","Page request")
		
def chec_schedule(userType):
	writeLog(DEST_APP,17,6,"schedule","-","Schedule checked")

FUNCTIONS = {'A':get_patient_data,'B':print_info,'C':set_appointment,'D':give_prescription,'E':update_patient_data,'F':reserve_operation_room,'G':alert_area,'H':request_transport_for_patient,'I':comunicate,'J':read_announcements,'K':add_announcements,'L':register_doc,'M':remove_doc,'N':set_schedule,'O':edit_wiki,'P':add_patient_data,'Q':read_wiki,'R':chec_schedule}
		
main()