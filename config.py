#!/usr/bin/python
'''
Main configuration file.

Nacho Mas January-2017
'''

import json
import commands

ixon={}
ixon['name']='ANTSY'
ixon['jpg']='ixon888.jpg'

apogee={}
apogee['name']='CENTU'
apogee['jpg']='apogee.jpg'

sbig={}
sbig['name']='TRACKER'
sbig['jpg']='sbig.jpg'

fli={}
fli['name']='CENTU1'
fli['jpg']='fliCobalt.jpg'

camera=ixon

debug=0
zmqShutterPort = 5556
zmqGPSPort = 5557
zmqTripPort = 5558
socketsPort = 9999
TripPort = 9998
httpPort= 5000

#socat command have to be launch before:
#'socat pty,link=/tmp/cronostamperCOM,raw TCP-LISTEN:27644,reuseaddr &'
# used only by zmqSerial.py now NOT USED.
#serialPortName='/tmp/cronostamperCOM'


#topic to be reported. 
#for pulse on open shutter (direct logic)
ShutterFlange="SHUTTER_LOW"
#for pulse on close shutter (inverted logic)
#ShutterFlange="SHUTTER_HIGH"

#SIGNAL_GPIO=11
SIGNAL_GPIO=18
PPS_GPIO=18
TRIP_GPIO=4
TRIP_WAVE_REF_GPIO=22

#some functions used in several places
def getSystemClockData():
	cmdrst=commands.getstatusoutput('ntpq -c kern')
	status=cmdrst[0]
	rst=cmdrst[1]
	if rst!='ntpq: read: Connection refused':
		out=rst.split('\n')[1:]
		res={}
		for line in out:
			dummy=line.split(':')
			if len(dummy)!=2:
				continue
			else:
				key=dummy[0]
				value=dummy[1]
				res[key]=value

		ppm=float(res['pll frequency'])
		pllOffset=float(res['pll offset'])
		maxError=float(res['maximum error'])
		Error=float(res['estimated error'])
	else:
        	ppm="0"
		pllOffset="9999."
        	maxError="9999."
		Error="9999."
		print "Warning: NTPD fail"

	cmdrst=commands.getstatusoutput('ntpq -c sysinfo')
	status=cmdrst[0]
	rst=cmdrst[1]
	if rst!='ntpq: read: Connection refused':
		out=rst.split('\n')[1:]
		res={}
		for line in out:
			dummy=line.split(':')
			if len(dummy)!=2:
				continue
			else:
				key=dummy[0]
				value=dummy[1]
				res[key]=value

		referenceID=res['reference ID'].strip()
	else:
		print "Warning: NTPD fail"
		referenceID="NTPD FAIL"

	if referenceID=='PPS':
		ppsOK=True
	else:
		ppsOK=False

	msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error,'ppsOK':ppsOK,'clkReferenceID':referenceID}
	return msg

def mogrify(topic, msg):
    """ json encode the message and prepend the topic """
    return topic + ' ' + json.dumps(msg)

def demogrify(topicmsg):
    """ Inverse of mogrify() """
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg 
