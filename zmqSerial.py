#!/usr/bin/python
'''
Server the event time througth 
a serial port

OBSOLETE BY mzqSocketServer.py!!
Nacho Mas January-2017
'''

import zmq
import time
import os, pty, serial
import subprocess
import commands
from config import *

if __name__ == '__main__':

	#socat command have to be launch before:
	#'socat pty,link=/tmp/cronostamperCOM,raw TCP-LISTEN:27644,reuseaddr &'
	context = zmq.Context()
	topicfilter = "SHUTTER_HIGH"
	socket = context.socket(zmq.SUB)
	#only one message (do not work with the stock version of zmq, works from ver 4.1.4)
	socket.setsockopt(zmq.CONFLATE, 1)
	socket.connect ("tcp://localhost:%s" % zmqShutterPort)
	socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

	ser = serial.Serial(serialPortName)
	while True:
		m= socket.recv()
		topic, msg  = demogrify(m)
		ser.write(msg['dateUTC']+'\n')
		ser.flush()
		print msg['dateUTC']
		time.sleep(0.1)


