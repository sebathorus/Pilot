from os import listdir
from os.path import isdir, isfile, join, exists
import sys
import time

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

DIR_BASE = "/var/www/html/datainst/"
nodelist = []
feed_id = "DemoFeed"
# Set to your Adafruit IO key & username below.
ADAFRUIT_IO_KEY      = 'own_adafruit_key'
ADAFRUIT_IO_USERNAME = 'own_adafruit_user'  # See https://accounts.adafruit.com
                                     # to find your username.

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print 'Connected to Adafruit IO!  Listening for DemoFeed changes...'
    # Subscribe to changes on a feed named DemoFeed. This feed is used to send commands from dashboard to RaspberryPi client
    client.subscribe('DemoFeed')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print 'Disconnected from Adafruit IO!'
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print 'Feed {0} received new value: {1}'.format(feed_id, payload)


# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()
client.loop_background()
# Now send new values every 15 seconds.

nodeconf = open("/home/pi/pilot/node_config.txt")
#node_config.txt contains pairing between nodes MAC addresses and AdafruitIO feeds names
for nodeidx in nodeconf:
	nodeidx2 = nodeidx.split()
	nodetup = (nodeidx2[0], nodeidx2[1])
	nodelist.append(nodetup)
nodeconf.close()

#print '\n'.join(str(p) for p in nodelist)

FILES_LIST = [f for f in listdir(DIR_BASE) if isfile(join(DIR_BASE, f))]
print FILES_LIST
print 'Publishing a new message every 20 seconds (press Ctrl-C to quit)...'
while True:
    #sourcefile is instant temperature log file - /var/www/html/MAC_tempinst - MAC is replaced with nodes MAC address
    for sourcefile in FILES_LIST:
	sourcefile = str(DIR_BASE) + sourcefile
	print "Sourcefile = ", sourcefile
	fh = open(sourcefile)
	for fileread in fh:
#		print fileread
		fileread2 = fileread.split(" ")
		value = fileread2[0]
		nodemac = fileread2[1]
#		print "Node MAC from temperature log file = ", nodemac
		for nodecheck in nodelist:
			nodemaclist = nodecheck[0]
			nodefeed = nodecheck[1]
			if nodemac == nodemaclist:
				feedname = nodefeed
#				print "Node MAC from list(config file) = ", nodemaclist
#				print "Node feed name = ", nodefeed
#		print value
		print 'Publishing {0} to {1} feed.'.format(value, feedname)
		client.publish(feedname, value)
	fh.close()
    time.sleep(20)
