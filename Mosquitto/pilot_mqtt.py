import time 
import sys
from datetime import datetime
from os import listdir 
from os.path import isdir, isfile, join, exists
import paho.mqtt.client as mqtt


DIR_BASEINST = "/var/www/html/datainst/"
DIR_BASEHIST = "/var/www/html/datahist/"
pilotIP = "aaa.bbb.ccc.ddd" - RaspberryPi IP address
receivedvaltemp = ""
receivedvalhum = ""
receivedvallight = ""



def on_connect(mqttc, obj, flags, rc):
	print("rc: "+str(rc))
	#client subscribe to all topics with names beginning with "sensorfeed/"
	mqttc.subscribe("sensorsfeed/#", 0)

def on_message(mqttc, obj, msg):
#	print everything published on "sensorfeed/" and not matching temperature, humidity, light or detection messages
	print(str(msg.payload))

def on_message_temperature(mqttc, obj, msg):
	global receivedvaltemp
	receivedvaltemp = str(msg.payload)
	recsplit = receivedvaltemp.split("=")
	tempval = recsplit[1]
	nodemac = recsplit[2]
	print "Node MAC from temperature feed = ", nodemac
	tempdatahist = DIR_BASEHIST + nodemac + "_temphist"
	tempdatainst = DIR_BASEINST + nodemac + "_tempinst"
#	fhtdh = file handler temp data hist	- this file store a log temperature values sent by nodes
#	if a log file for temperature data of a node did not exist, it is created - nodes can be added on the fly without previous configuration
	if not exists(tempdatahist):
		fhtdh = open(tempdatahist,'w')
		fhtdh.close()
	fhtdh = open(tempdatahist,'a')
	fhtdh.write(time.strftime("%D-%H:%M:%S ") + tempval + '\n')
	fhtdh.close()

#   fhtdi = file handler temp data inst	- this file store only the last temperature value sent by nodes
#	being an instantaneous value, the content of the file is overwritten every time
	fhtdi = open(tempdatainst,'w')
    fhtdi.write(tempval + " " + nodemac)
    fhtdi.close()

	print "Temperature ", tempval
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

# client follow and process only messages published on following feeds, by calling corresponding functions
mqttc.message_callback_add("sensorsfeed/temperature/#", on_message_temperature)
mqttc.message_callback_add("sensorsfeed/humidity/#", on_message_humidity)
mqttc.message_callback_add("sensorsfeed/light/#", on_message_light)
mqttc.message_callback_add("sensorsfeed/detection/#", on_message_detection)

mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

#	client connect to RaspberryPi broker
mqttc.connect(pilotIP, 1883, 60)
mqttc.loop_start()

try:
	while True:
		print receivedvaltemp
		time.sleep(10)

except KeyboardInterrupt:
       print 'Bye'
       mqttc.loop_stop()
