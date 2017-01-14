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
fli['name']='FLI Cobalt'
fli['jpg']='fliCobalt.jpg'

camera=fli

debug=0
zmqShutterPort = 5556
zmqGPSPort = 5557

socketsPort = 9999
httpPort= 5000

#socat command have to be launch before:
#'socat pty,link=/tmp/cronostamperCOM,raw TCP-LISTEN:27644,reuseaddr &'
serialPortName='/tmp/cronostamperCOM'


#topic to be reported. In this case the end of the SIGNAL pulse
ShutterFlange="SHUTTER_LOW"

SIGNAL_GPIO=11
PPS_GPIO=18

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
		clkStatus="OK"
	else:
        	ppm="NTPD FAIL"
		pllOffset="NTPD FAIL"
        	maxError="NTPD FAIL"
		Error="NTPD FAIL"
		clkStatus="FAIL"
		print "Warning: NTPD fail"

	msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error,'clkStatus':clkStatus}
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
