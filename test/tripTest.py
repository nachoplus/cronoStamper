#!/usr/bin/python
'''
Trip test program
Nacho Mas June-2018
'''

import zmq
import time
import json
import datetime
import random

def demogrify(topicmsg):
    """ Inverse of mogrify() """
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg

zmqShutterPort = 5556
zmqTripPort = 5558
ShutterFlange="SHUTTER_LOW"
    

context = zmq.Context()

socketS = context.socket(zmq.SUB)
#socketS.setsockopt(zmq.CONFLATE, 1)
socketS.connect ("tcp://cronostamper:%s" % zmqShutterPort)
topicfilter = ShutterFlange
socketS.setsockopt(zmq.SUBSCRIBE, topicfilter)

#  Socket to talk to server

socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:%s" % zmqTripPort)

#  Do 10 requests, waiting each time for a response
for request in range(100):
    r=random.random()
    #RTCtrip=str(int(time.time())+2+0.15)
    RTCtrip=int(time.time())+2.96
    socket.send(str(RTCtrip))
    time.sleep(1)	

    message = socket.recv()
    topic, msg  = demogrify(socketS.recv())
    unixTimeStamp=datetime.datetime.fromtimestamp(msg['unixUTC'])
    alarm=datetime.datetime.fromtimestamp(float(RTCtrip))
    print alarm,',',RTCtrip-int(RTCtrip),',',RTCtrip,',',msg['unixUTC'],',',abs(unixTimeStamp-alarm).total_seconds()*1000000
    #print("Received reply %s [ %s ]" % (request, message))
