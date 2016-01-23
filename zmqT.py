#!/usr/bin/python

import sys
import zmq
import time
import json

from config import *

    
# Socket to talk to server
context = zmq.Context()
socket0 = context.socket(zmq.SUB)
socket1 = context.socket(zmq.SUB)
#socket.setsockopt(zmq.CONFLATE, 1)
socket0.connect ("tcp://localhost:%s" % zmqPort)
socket1.connect ("tcp://localhost:%s" % zmqPort)
topicfilter = "SHUTTER_HIGH"
socket0.setsockopt(zmq.SUBSCRIBE, topicfilter)
topicfilter = "SYSTEM_CLOCK"
socket1.setsockopt(zmq.SUBSCRIBE, topicfilter)

# Process
while True:
	    	topic, msg  = demogrify(socket0.recv())
		if topic =='SHUTTER_HIGH':
			print "%f" % msg['unixUTC']
		else:
			print msg
		#time.sleep(5)

      
