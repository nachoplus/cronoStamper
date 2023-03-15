#!/usr/bin/python
'''
Main configuration file.

Nacho Mas January-2017
'''

import json
import datetime 
import logging
import subprocess


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

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(module)s:%(levelname)s:%(message)s')

#some functions used in several places
def getstatusoutput(*args, **kwargs):
    p = subprocess.Popen(*args, **kwargs,shell=True, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr
    
def getSystemClockData():
        return chrony_getSystemClockData()

def chrony_getSystemClockData():
	#cmdrst=getstatusoutput('chronyc -n sources')
	#if cmdrst[0]==0:	
	#	chrony_fail=False
	#	referenceID=False
	#	for s in cmdrst[1].decode().split('\n'):
	#		logging.debug(s)
	#		if len(s)==0:
	#			continue
	#		if s[1]=='*':
	#			referenceID=s.split(' ')[1]
	#	if referenceID==False:
	#		referenceID="Not any TIME SOURCE"
	#		logging.warning(referenceID)
	#		chrony_fail=True
	#else:
	#	logging.warning('chrony -n sources FAIL')
	#	chrony_fail=True   
	#	referenceID="Chrony FAIL"


	if True:
		cmdrst=getstatusoutput('chronyc -n tracking')
		#logging.info(cmdrst)		
		if cmdrst[0]==0:	
			result={}
			for s in cmdrst[1].decode().split('\n'):
				if len(s)==0:
					continue
				dummy=s.split(':',1)
				k=dummy[0].strip()
				v=dummy[1].strip().replace('seconds','').strip()
				result[k]=v
				logging.debug(f'{k}:{v}')
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
			logging.debug(result)
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
			referenceID=result['Reference ID']
			if 'PPS' in result['Reference ID'] and result['lastPPS']<datetime.timedelta(seconds=10):
				ppsOK=True
			else:
				ppsOK=False
				referenceID=f"PPS({result['lastPPS'].seconds}s old)"
			pllOffset=round(result['RMS offset']*1000000,3)
		else:	
			logging.warning('chronyc -n tracking FAIL')		
			logging.debug(f"{cmdrst}")			  
			ppsOK=False
			ppm=0
			pllOffset="9999."
			maxError="9999."
			Error="9999."
			referenceID='Chrony FAIL'


	msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error,'ppsOK':ppsOK,'clkReferenceID':referenceID}
	logging.debug(msg)
	return msg

def ntpd_getSystemClockData():
	cmdrst=getstatusoutput('ntpq -c kern')
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
		logging.warning("Warning: NTPD fail")

	cmdrst=getstatusoutput('ntpq -c sysinfo')
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
		logging.warning("Warning: NTPD fail")
		referenceID="NTPD FAIL"

	if referenceID=='PPS':
		ppsOK=True
	else:
		ppsOK=False

	msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error,'ppsOK':ppsOK,'clkReferenceID':referenceID}
	return msg

def mogrify(topic, msg):
    """ json encode the message and prepend the topic """
    return f'{topic} {json.dumps(msg)}'.encode()

def demogrify(topicmsg_):
    """ Inverse of mogrify() """
    topicmsg=topicmsg_.decode()
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg 
    
if __name__ == '__main__':
        chrony_getSystemClockData()

