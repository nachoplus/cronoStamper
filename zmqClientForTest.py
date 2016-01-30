#!/usr/bin/python
#Simple remote zmq client to record test data 
#to run in the PC side
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
		print "%0.6f" %msg['unixUTC']
		#time.sleep(5)

      
