#!/usr/bin/python
import json
import commands

debug=0
zmqPort = 5556
zmqGPSPort = 5557

socketsPort = 9999
httpPort= 5000

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
		status="OK"
	else:
        	ppm=0
		pllOffset=0
        	maxError=16
		Error=16
		status="NTPD fail"
		print "Warning: NTPD fail"

	msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error,'status':status}
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
