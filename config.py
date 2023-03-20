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

camera={u'name': u'cronostamper', u'jpg': u'moon_big_small.png'}

debug=0
zmqShutterPort = 5556
zmqGPSPort = 5557
zmqTriggerPort  = 5558
shutterPort = 9999
triggerPort = 9998
httpPort = 5000
pingPort = 5555

ports={
	'zmqShutterPort' : zmqShutterPort,
	'zmqGPSPort' : zmqGPSPort,
	'zmqTriggerPort' : zmqTriggerPort ,
	'shutterPort' : shutterPort,
	'triggerPort' : triggerPort,
	'httpPort' : httpPort,
	'pingPort':pingPort
}

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
	cmdrst=getstatusoutput('chronyc -n tracking')
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
		if 'PPS' in result['Reference ID']:
			if result['lastPPS']<datetime.timedelta(seconds=10):
				ppsOK=True		
				referenceID='PPS'
			else:
				ppsOK=False
				referenceID=f"PPS({result['lastPPS'].seconds}s old)"
		else:
			ppsOK=False						
		pllOffset=round(result['RMS offset']*1000000,3)
	else:	
		logging.warning('chronyc -n tracking FAIL')		
		logging.debug(f"{cmdrst}")			  
		ppsOK=False
		ppm=0
		pllOffset=9999.
		maxError=9999.
		Error=9999.
		referenceID='Chrony FAIL'


	msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error,'ppsOK':ppsOK,'clkReferenceID':referenceID}
	logging.debug(msg)
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
        print(getSystemClockData())

