#!/usr/bin/python
'''
Trip test program
Nacho Mas June-2018
'''

import zmq
import time

context = zmq.Context()

#  Socket to talk to server

socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5558")

#  Do 10 requests, waiting each time for a response
for request in range(10):
    RTCtrip=str(time.time()+1)
    socket.send(RTCtrip)
    time.sleep(2)	
    #  Get the reply.
    message = socket.recv()
    print("Received reply %s [ %s ]" % (request, message))
