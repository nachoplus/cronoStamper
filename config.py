#!/usr/bin/python
'''
Main configuration file.

Nacho Mas January-2017
'''

import json
import commands
import datetime 

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

camera={u'name': u'stamper00', u'jpg': u'moon_big_small.png'}

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

SIGNAL_GPIO=11
#SIGNAL_GPIO=18
PPS_GPIO=18
TRIP_GPIO=4
TRIP_WAVE_REF_GPIO=22

#some functions used in several places
def getSystemClockData():
        return chrony_getSystemClockData()

def chrony_getSystemClockData():
        cmdrst=commands.getstatusoutput('chronyc -n sources')
	if cmdrst[0]==0:	
                chrony_fail=False
                referenceID=False
	        for s in cmdrst[1].split('\n'):
	                if s[1]=='*':
                                referenceID=s.split(' ')[1]
                if referenceID==False:
                        referenceID="Not any TIME SOURCE"
                        chrony_fail=True
        else:
                chrony_fail=True   
                referenceID="Chrony FAIL"
	cmdrst=commands.getstatusoutput('chronyc -n tracking')
	if cmdrst[0]==0 and not chrony_fail:	
        	chrony_fail=False
                result={}
	        for s in cmdrst[1].split('\n'):
	                dummy=s.split(':',1)
	                k=dummy[0].strip()
	                v=dummy[1].strip().replace('seconds','').strip()
	                result[k]=v
	        result.update({'Ref time (UTC)':datetime.datetime.strptime(result['Ref time (UTC)'],'%a %b %d %H:%M:%S %Y')})  
	        result.update({'lastPPS':datetime.datetime.now()-result['Ref time (UTC)']})      
	        result.update({'Stratum':int(result['Stratum'])})
	        result.update({'Root delay':float(result['Root delay'])})
	        result.update({'Root dispersion':float(result['Root dispersion'])})
                result.update({'Update interval':float(result['Update interval'])})	
	        result.update({'Last offset':float(result['Last offset'])})
	        result.update({'RMS offset':float(result['RMS offset'])})
	        result.update({'Residual freq':float(result['Residual freq'].replace(' ppm',''))})	#ppm	
	        result.update({'Skew':float(result['Skew'].replace(' ppm',''))})	#ppm
	        print(result)
	        if 'fast' in result['System time']:
	                system_time_sign=-1
	        else:
                	system_time_sign=1        
	        result['System time error']=float(result['System time'].split(' ')[0])*system_time_sign
	        if 'fast' in result['Frequency']:
	                Frequency_sign=-1
	        else:
                	Frequency_sign=1        
	        result['ppm']=float(result['Frequency'].split(' ')[0])*Frequency_sign	
	        
	        ppm=result['ppm']
	        maxError=round((result['Root dispersion']+result['Root delay']/2)*1000000,3)
	        Error=round(result['System time error']*1000000,3)
	        if 'PPS' in result['Reference ID'] and result['lastPPS']<datetime.timedelta(seconds=10):
                        ppsOK=True
                else:
                        ppsOK=False
                        referenceID='PPS('+str(result['lastPPS'].seconds)+'s old)'
                pllOffset=round(result['RMS offset']*1000000,3)
	else:
                chrony_fail=True	           
                
        if chrony_fail:
        	print(cmdrst)	
        	ppsOK=False
        	ppm=0
		pllOffset="9999."
        	maxError="9999."
		Error="9999."
		print "Warning: NTPD fail"

	msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error,'ppsOK':ppsOK,'clkReferenceID':referenceID}
	print(msg)
	return msg

def ntpd_getSystemClockData():
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
        	ppm=-9.2
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
    
if __name__ == '__main__':
        chrony_getSystemClockData()

