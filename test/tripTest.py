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
socket.connect("tcp://cronostamper:%s" % zmqTripPort)

#  Do 10 requests, waiting each time for a response
RTCtripList=[]
for request in range(100):
    r=random.random()
    if r>0.90:
	r=0.90
    RTCtrip=int(time.time())+2+0.0+request
    #RTCtrip=int(time.time())+2.+request+r
    strRTCtrip= "%0.6f" % RTCtrip
    RTCtripList.append(RTCtrip)
    socket.send('UNIXTIME '+strRTCtrip)
    #time.sleep(1)	
    message = socket.recv()
    #print message



for RTCtrip in sorted(RTCtripList):
    topic, msg  = demogrify(socketS.recv())
    unixTimeStamp=datetime.datetime.fromtimestamp(msg['unixUTC'])
    alarm=datetime.datetime.fromtimestamp(float(RTCtrip))
    print alarm,',',RTCtrip-int(RTCtrip),',',"%0.6f" % RTCtrip,',',"%0.6f" % msg['unixUTC'],',',(unixTimeStamp-alarm).total_seconds()*1000000

