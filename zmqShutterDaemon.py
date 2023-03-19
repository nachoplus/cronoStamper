#!/usr/bin/python3
'''
Get the timestamp of SIGNAL activation and 
send a msg througth zmq.PUB

Nacho Mas January-2017
'''
import pigpio
import time
import datetime
import zmq
import json

from config import *


RTCsecond=0
RTCtick=0

ppm=0
shutterOK=False
lastHIGH=0
lastLOW=0

pi=pigpio.pi()



#get the PLL system clock correction in PPM
def getPPM():
	global ppm
	clkData=getSystemClockData()
	ppm=float(clkData['ppm'])



#get data to correlate system time with the CPU ticks
#use PPS signal interrupt to get tick:UTCtime point
def discipline(gpio, level, tick):
	global RTCsecond,RTCtick,ppm
	diff=pigpio.tickDiff(RTCtick,tick)
	now=time.time()
	getPPM()
	#trying to avoid spurius signals
	#not update if there is less than 0.9999 seconds
	if diff <999900:
		logging.warning(f"Discipline Spuck!:{diff}")
		return
	RTCsecond=int(round(now))
	logging.debug(f'PPS DISCIPLINE RTCsecond:{RTCsecond} RTCtick:{RTCtick} tick:{tick} diff:{diff}')
	RTCtick=tick

	

#corrected RTCsecond,RTCtick and ppm 
def ticks2unixUTC(tick):
	global RTCsecond,RTCtick,ppm,shutterOK
	nowSecond=int(round(time.time()))
	#OK if PPS signal is not far than 1second
	if nowSecond-RTCsecond<2:
		shutterOK=True
	else:
		shutterOK=False
	tickOffset=pigpio.tickDiff(RTCtick, tick)
	#print(RTCsecond,RTCtick,tick,tickOffset)
	bias=ppm*(tickOffset/1000000.)
	UTC=float(RTCsecond)+(tickOffset+bias)/1000000.
	#print (RTCsecond,ppm,tick,tickOffset,pllOffset,bias,UTC)
	return UTC

#get UTC timestamp for the incoming pulse
def GPIOshutter(gpio, level, tick):
	global lastHIGH,lastLOW,shutterOK
	unixUTC=ticks2unixUTC(tick)
	if level == 1:
		#INVERTED LOGIC
		#Inform when shutter signal goes to HIGH.
		#start time = lastLOW
		#Pulse timespan from last HIGH flange
		topic="SHUTTER_HIGH"
		lastHIGH=unixUTC
		pulse=unixUTC-lastLOW
		unixUTC_= lastLOW
	else:
		#DIRECT LOGIC
		#Inform when shutter signal goes to HIGH.
		#start time = lastHIGH
		#Pulse timespan from last HICH flange
		topic="SHUTTER_LOW"
		lastLOW=unixUTC
		pulse=unixUTC-lastHIGH
		unixUTC_= lastHIGH

	pulse=round(pulse,6)
	dateUTC=unixTime2date(unixUTC_)
	MJD=unixTime2MJD(unixUTC_)
	msg = {'tick':tick,'level':level,'unixUTC':unixUTC_,'dateUTC':dateUTC,'MJD':MJD,'pulse':pulse,'shutterOK':shutterOK}
	logging.info(f'SHUTTER TRIPPED:{dateUTC} PULSE:{pulse:05.6f} LEVEL:{level} OK:{shutterOK}')
	logging.debug(f'msg:{msg}')
	socket.send(mogrify(topic,msg))




def unixTime2date(unixtime):
        #dateStr = str(datetime.datetime.fromtimestamp(unixtime))
        d = datetime.datetime.fromtimestamp(unixtime)
        dateStr=d.strftime("%Y-%m-%d %H:%M:%S.%f")
        return dateStr


def unixTime2MJD(unixtime):
	return ( unixtime / 86400.0 ) + 2440587.5 - 2400000.5

if __name__ == '__main__':
	logging.info('STARTING...')
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	zmq_end_point=f"tcp://*:{zmqShutterPort}"
	socket.bind(zmq_end_point)
	logging.info(f'Started zmq Shutter endpoint -> {zmq_end_point}')
	logging.info(f'SIGNAL_GPIO:{SIGNAL_GPIO} PPS_GPIO:{PPS_GPIO}')		
	getSystemClockData()
	logging.info(f'setting SIGNAL_GPIO and PPS_GPIO pull down resitors')		
	pi.set_pull_up_down(SIGNAL_GPIO, pigpio.PUD_DOWN)
	pi.set_pull_up_down(PPS_GPIO, pigpio.PUD_DOWN)
	logging.info(f'Registe GPIOs Callbacks')			
	cb1 = pi.callback(SIGNAL_GPIO, pigpio.EITHER_EDGE, GPIOshutter)
	cb2 = pi.callback(PPS_GPIO, pigpio.RISING_EDGE, discipline)
	while True:
	    time.sleep(1)


