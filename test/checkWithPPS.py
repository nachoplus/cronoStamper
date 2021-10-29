#!/usr/bin/env python
'''
Check Cronostamper. Connect the PPS signal of an
independent GPS chip to the signal Cronostamper connector.

 
Nacho Mas January-2017
'''
cronostamper="192.168.2.103"

import sys
import zmq
import time,datetime
import json
import matplotlib.pyplot as plt
import numpy as np

def demogrify(topicmsg):
    topicmsg=topicmsg.decode("utf-8") 
    #print(f'{topicmsg}')
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
socket.connect (f"tcp://{cronostamper}:{zmqShutterPort}")
topicfilter = ShutterFlange
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

#Set the period of PPS signal
#usualy 1s but it could be change 
#using the uBlox control software
#in microsencond
period=1000000
delta=datetime.timedelta(microseconds=period)
#Get 100 samples
maxsamples=30
samples=[]
print( "Geting ",maxsamples," samples. Pulse width:",period," us. Estimated time:",period*maxsamples/1000000.,"seconds")
for i in range(maxsamples):
               topic, msg  = demogrify(socket.recv())
               unixTimeStamp=datetime.datetime.fromtimestamp(msg['unixUTC'])
		#dateUTC=datetime.datetime.strptime(msg['dateUTC'],'%Y-%m-%d %H:%M:%S.%f')+3600*datetime.timedelta(seconds=1)
               if i==0:
                       trun=int(round(msg['unixUTC']*1000000/period))*period/1000000.
                       first_sample=datetime.datetime.fromtimestamp(trun)
               ref_timestamp=first_sample+i*delta
               #errDATE=(dateUTC-ref_timestamp).total_seconds()
               err=(unixTimeStamp-ref_timestamp).total_seconds()
               errUNIX=(msg['unixUTC']-(trun+i*period/1000000.))
               print(". "+str(i)+" ERR: "+str(err))
               samples.append((ref_timestamp,unixTimeStamp,err,errUNIX))
	       #print i,ref_timestamp,unixTimeStamp,err
	       #time.sleep(5)

data = np.asarray(samples)
errors = data[:,3]
np.savetxt(f"{cronostamper}_errors.csv", data[:,[2,3]], delimiter=",")
print ("==== RESULTS ====")
print( "Mean Err:",errors.mean())
print( "Max  Err:",errors.max())
print( "Min  Err:",errors.min())
print( "STD Err:",errors.std())
print( "HISTOGRAM")
#print np.histogram(errors)

plt.clf()
plt.hist(errors*1000000)
plt.title(f"{cronostamper}_Error Histogram. Samples:{maxsamples}")
plt.xlabel("Error [microseconds]")
plt.ylabel("Frequency")
plt.savefig(f"{cronostamper}_error_histo.png",dpi=600)

plt.clf()
plt.xlabel("samples")
plt.ylabel(f"{cronostamper}_Error [microseconds]. Samples:{maxsamples}")
plt.plot(errors*1000000)
plt.savefig(f"{cronostamper}_error.png",dpi=600)

