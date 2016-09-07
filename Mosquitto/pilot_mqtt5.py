import time 
import sys
from datetime import datetime
from os import listdir 
from os.path import isdir, isfile, join, exists
import paho.mqtt.client as mqtt


DIR_BASEINST = "/var/www/html/datainst/"
DIR_BASEHIST = "/var/www/html/datahist/"
nodelist = []
pilotIP = "192.168.1.150"
nodemac = ""
tempval = "0"
receivedvaltemp = ""
receivedvalhum = ""
receivedvallight = ""



def on_connect(mqttc, obj, flags, rc):
	print("rc: "+str(rc))
	mqttc.subscribe("sensorsfeed/#", 0)

def on_message(mqttc, obj, msg):
#	global value
#	value = str(msg.payload)
#	print everything 
	print(str(msg.payload))

def on_message_temperature(mqttc, obj, msg):
#	global receivedvaltemp
	global tempval
	receivedvaltemp = str(msg.payload)
	print receivedvaltemp
	recsplit = receivedvaltemp.split("=")
	tempval = recsplit[1]
	nodemac = recsplit[2]
#	print "Node MAC from temperature feed = ", nodemac
	tempdatahist = DIR_BASEHIST + nodemac + "_temphist"
	tempdatainst = DIR_BASEINST + nodemac + "_tempinst"
#	fhtdh = file handler temp data hist	
	if not exists(tempdatahist):
		fhtdh = open(tempdatahist,'w')
		fhtdh.close()
	fhtdh = open(tempdatahist,'a')
	fhtdh.write(time.strftime("%D-%H:%M:%S ") + tempval + '\n')
	fhtdh.close()

#       fhtdi = file handler temp data inst
	fhtdi = open(tempdatainst,'w')
        fhtdi.write(tempval + " " + nodemac)
        fhtdi.close()

#	print "Temperature ", tempval
#        print(str(msg.payload))

def on_message_humidity(mqttc, obj, msg):
	global receivedvalhum
        receivedvalhum = str(msg.payload)
        recsplit = receivedvalhum.split("=")
        humval = recsplit[1]
        nodemac = recsplit[2]
        print "Node MAC from humidity feed = ", nodemac
        humdatahist = DIR_BASEHIST + nodemac + "_humhist"
        humdatainst = DIR_BASEINST + nodemac + "_huminst"
#       fhhdh = file handler humidity data hist
        if not exists(humdatahist):
                fhhdh = open(humdatahist,'w')
                fhhdh.close()
        fhhdh = open(humdatahist,'a')
        fhhdh.write(time.strftime("%D-%H:%M:%S ") + humval + '\n')
        fhhdh.close()

#       fhhdi = file handler humidity data inst
        fhhdi = open(humdatainst,'w')
        fhhdi.write(humval)
        fhhdi.close()
	print "Humidity ",humval


def on_message_light(mqttc, obj, msg):
        print("Light intensity "+str(msg.payload))

def on_message_detection(mqttc, obj, msg):
        print("Movement detected "+str(msg.payload))

def on_publish(mqttc, obj, mid):
        print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

mqttc = mqtt.Client()

mqttc.on_message = on_message
mqttc.message_callback_add("sensorsfeed/temperature/#", on_message_temperature)
mqttc.message_callback_add("sensorsfeed/humidity/#", on_message_humidity)
mqttc.message_callback_add("sensorsfeed/light/#", on_message_light)
mqttc.message_callback_add("sensorsfeed/detection/#", on_message_detection)

mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqttc.connect(pilotIP, 1883, 60)
mqttc.loop_start()

#nodeconf = open("/home/pi/pilot/node_config.txt")
#node_config.txt contains pairing between nodes MAC addresses and AdafruitIO feeds names
#for nodeidx in nodeconf:
#	nodeidx2 = nodeidx.split()
#	nodetup = (nodeidx2[0], nodeidx2[1])
#	nodelist.append(nodetup)
#nodeconf.close()

try:
	while True:
#		test = float(tempval)
#		test = 25
		print "tempval = ", tempval
		if float(tempval) < 22:
			print "Temperature is low", tempval
			print "Node MAC from temperature feed = ", nodemac
		if (float(tempval) > 22) and (float(tempval) < 25):
                        print "Temperature is normal", tempval
                        print "Node MAC from temperature feed = ", nodemac
		if float(tempval) > 25:
                        print "Temperature is high", tempval
                        print "Node MAC from temperature feed = ", nodemac
		time.sleep(20)

except KeyboardInterrupt:
       print 'Bye'
       mqttc.loop_stop()
