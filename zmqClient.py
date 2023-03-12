#!/usr/bin/python
'''
Example of zmq client.
Can be used to record test data on
remote PC

Nacho Mas January-2017
'''

import sys
import zmq
import time
import json

from config import *

    
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
#socket.setsockopt(zmq.CONFLATE, 1)
socket.connect ("tcp://cronostamper:%s" % zmqShutterPort)
topicfilter = ShutterFlange
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

# Process
while True:
	    	topic, msg  = demogrify(socket.recv())
		print("%f" % msg['unixUTC'])
		#time.sleep(5)

      
