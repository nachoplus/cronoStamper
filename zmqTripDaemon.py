#!/usr/bin/python
'''
Get the timestamp of SIGNAL activation and 
send a msg througth zmq.PUB

Nacho Mas January-2017
'''
import pigpio
import time
import datetime
import zmq
import commands
import json

from config import *

TRIP_WAVE_REF_GPIO=4

RTCsecond=0
RTCtick=0
waveTick=0
lastSecondTicks=0
slash=0

ppm=0
lastHIGH=0
lastLOW=0

pi=pigpio.pi()


def checkWaveBuffer():
	maxCBS=pi.wave_get_max_cbs()
	maxPulse=pi.wave_get_max_pulses()
	maxMicros=pi.wave_get_max_micros()

	CBS=pi.wave_get_cbs()
	Pulse=pi.wave_get_pulses()
	Micros=pi.wave_get_micros()
	print "CBS, Pulses, Micros:",CBS,'/',maxCBS,Pulse,'/',maxPulse,Micros,'/',maxMicros

def defwave(gpio,preamble,pulse,postamble):
	syncwave=[]	
	syncwave.append(pigpio.pulse(0,1 << gpio, preamble))
	syncwave.append(pigpio.pulse(1 << gpio,0, pulse))
	syncwave.append(pigpio.pulse(0, 1 << gpio, postamble))
	pi.wave_add_generic(syncwave)


def sendWave(init=False):
	global RTCsecond,RTCtick,ppm,lastSecondTicks,slash
	print lastSecondTicks
	pulse=20000
	preamble=0
	'''
	if init or lastSecondTicks==0 :
		wavelength=1000000
		print "sendWave init"
	else:
		wavelength=lastSecondTicks
	if wavelength>=1100000:
		print "PPS restart. "
		wavelength=1000000
	'''
	wavelength=1000000-ppm
	postamble=(wavelength-pulse)-slash
	print TRIP_WAVE_REF_GPIO,preamble,pulse,postamble		
	defwave(TRIP_WAVE_REF_GPIO,preamble,pulse,postamble)
	wid= pi.wave_create()
	print "WID:",wid,ppm
	pi.wave_send_using_mode(wid, pigpio.WAVE_MODE_ONE_SHOT_SYNC)
	if wid>=9:
		for i in range(10):
			pi.wave_delete(i)
	#checkWaveBuffer()

def getWaveTick(gpio, level, tick):
	global waveTick,slash,ppm
	wavelength=1000000-ppm
	waveTick=tick
	slash=(pigpio.tickDiff(RTCtick,waveTick) % wavelength)
	print slash
	if slash >=600000:
		print "PPS restart. "
		slash=(slash-wavelength)/6
	#print "WaveTick",waveTick
	sendWave()


#get the PLL system clock correction in PPM
def getPPM():
	global ppm
	clkData=getSystemClockData()
       	ppm=float(clkData['ppm'])




#get data to correlate system time with the CPU ticks
#use PPS signal interrupt to get tick:UTCtime point
def discipline(gpio, level, tick):
	global RTCsecond,RTCtick,ppm,lastSecondTicks
	lastSecondTicks=pigpio.tickDiff(RTCtick,tick)
	now=time.time()
	getPPM()
	#trying to avoid spurius signals
	#not update if there is less than 0.9999 seconds
	if lastSecondTicks <999900:
		print "Spuck!",lastSecondTicks
		return
	RTCsecond=int(round(now))
	#print (now,RTCsecond,RTCtick,tick,diff,lastSecondTicks)
	RTCtick=tick
	if not pi.wave_tx_busy():
		sendWave(True)	


	

#corrected RTCsecond,RTCtick and ppm 
def ticks2unixUTC(tick):
	global RTCsecond,RTCtick,ppm
	tickOffset=pigpio.tickDiff(RTCtick, tick)
	print RTCsecond,RTCtick,tick,tickOffset
	bias=ppm*(tickOffset/1000000.)
	UTC=float(RTCsecond)+(tickOffset+bias)/1000000.
	#print (RTCsecond,ppm,tick,tickOffset,pllOffset,bias,UTC)
	return UTC

#get UTC timestamp for the incoming pulse
def GPIOshutter(gpio, level, tick):
	global lastHIGH,lastLOW
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
	msg = {'tick':tick,'level':level,'unixUTC':unixUTC_,'dateUTC':dateUTC,'MJD':MJD,'pulse':pulse}
	socket.send(mogrify(topic,msg))

	if debug:
		if level == 1:
			print "HIGH:",
		else:
			print "LOW: ",
		print msg
		print unixTime2date(unixUTC)
		print "%.12f" % unixTime2MJD(unixUTC)



def unixTime2date(unixtime):
	d = str(datetime.datetime.fromtimestamp(unixtime))
	return d

def unixTime2MJD(unixtime):
	return ( unixtime / 86400.0 ) + 2440587.5 - 2400000.5

if __name__ == '__main__':
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:%s" % zmqTripPort)
	getSystemClockData()
	pi.wave_clear()
	pi.set_mode(TRIP_WAVE_REF_GPIO,pigpio.OUTPUT)
	print pi.get_mode(TRIP_WAVE_REF_GPIO), pi.get_mode(PPS_GPIO)
	pi.set_pull_up_down(TRIP_WAVE_REF_GPIO, pigpio.PUD_DOWN)
	pi.set_pull_up_down(PPS_GPIO, pigpio.PUD_DOWN)
	cb1 = pi.callback(TRIP_WAVE_REF_GPIO, pigpio.RISING_EDGE, getWaveTick)
	cb2 = pi.callback(PPS_GPIO, pigpio.RISING_EDGE, discipline)
	while True:
 		time.sleep(1)



