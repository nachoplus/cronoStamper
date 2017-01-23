#!/usr/bin/python
'''
Check Cronostamper. Connect the PPS signal of an
independent GPS chip to the signal Cronostamper connector.

 
Nacho Mas January-2017
'''

import sys
import zmq
import time,datetime
import json
import matplotlib.pyplot as plt
import numpy as np

def demogrify(topicmsg):
    """ Inverse of mogrify() """
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg

zmqShutterPort = 5556
ShutterFlange="SHUTTER_LOW"
    
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
#socket.setsockopt(zmq.CONFLATE, 1)
socket.connect ("tcp://cronostamper:%s" % zmqShutterPort)
topicfilter = ShutterFlange
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

#Set the period of PPS signal
#usualy 1s but it could be change 
#using the uBlox control software
#in microsencond
period=1000000
delta=datetime.timedelta(microseconds=period)
#Get 100 samples
maxsamples=10
samples=[]
print "Geting ",maxsamples," samples. Pulse width:",period," us. Estimated time:",period*maxsamples/1000000.,"seconds"
for i in range(maxsamples):
	    	topic, msg  = demogrify(socket.recv())
		unixTimeStamp=datetime.datetime.fromtimestamp(msg['unixUTC'])
		if i==0:
			trun=int(msg['unixUTC']*1000000/period)*period/1000000.
			first_sample=datetime.datetime.fromtimestamp(trun)
		ref_timestamp=first_sample+i*delta
		err=(unixTimeStamp-ref_timestamp).total_seconds()
		samples.append((ref_timestamp,unixTimeStamp,err))
		#print i,ref_timestamp,unixTimeStamp,err
		#time.sleep(5)

errors = np.asarray(samples)[:,2]
print "==== RESULTS ===="
print "Mean Err:",errors.mean()
print "Max  Err:",errors.max(),
print "Min  Err:",errors.min(),
print "STD Err:",errors.std()
print "HISTOGRAM"
#print np.histogram(errors)

plt.clf()
plt.hist(errors*1000000,bins=7)
plt.title("Error Histogram")
plt.xlabel("Error [microseconds]")
plt.ylabel("Frequency")
plt.savefig("error_histo.png",dpi=600)

plt.clf()
plt.xlabel("samples")
plt.ylabel("Error [microseconds]")
plt.plot(errors*1000000)
plt.savefig("error.png",dpi=600)

