#!/usr/bin/python

import sys
import zmq
import time
import json

from config import *

    
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
#socket.setsockopt(zmq.CONFLATE, 1)
socket.connect ("tcp://localhost:%s" % zmqPort)
topicfilter = ""
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

# Process
while True:
	    	topic, msg  = demogrify(socket.recv())
		print msg
		#time.sleep(5)

      
