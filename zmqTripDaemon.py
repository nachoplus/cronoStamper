#!/usr/bin/python
'''
Trip a programe trigger signal
Nacho Mas June-2018
'''
import pigpio
import time
import datetime
import zmq
import commands
import json

from config import *


RTCsecond=0
RTCtick=0
waveTick=0
lastSecondTicks=0
slash=0
RTCtrip=0

ppm=0
lastHIGH=0
lastLOW=0

onetwo=True

pi=pigpio.pi()

def trip():
	global RTCtrip,RTCsecond
	delta=RTCtrip-ticks2unixUTC(waveTick)
	print "RTC:",RTCtrip,RTCsecond,delta
	if delta>=1. and delta<2. :
		print "FIRE!"
		return True
	else:
		return False

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


def sendWave():
	global RTCsecond,RTCtick,ppm,lastSecondTicks,slash
	pulse=100000
	preamble=0
	wavelength=1000000-ppm
	postamble=(wavelength-pulse)-slash
	defwave(TRIP_WAVE_REF_GPIO,preamble,pulse,postamble)
	if trip():
		preamble=(RTCtrip-int(RTCtrip))*(wavelength)+5
		postamble=(wavelength-pulse)-slash-preamble
		if postamble<0:
			postamble=0
		print "TRIP",preamble,pulse,postamble,RTCsecond
		defwave(TRIP_GPIO,preamble,pulse,postamble)
	wid= pi.wave_create()
	#print lastSecondTicks,"WID:",wid,ppm,TRIP_WAVE_REF_GPIO,preamble,pulse,postamble,wavelength
	pi.wave_send_using_mode(wid, pigpio.WAVE_MODE_ONE_SHOT_SYNC)
	if wid>=5:
		for i in range(6):
			pi.wave_delete(i)
	#checkWaveBuffer()

def getWaveTick(gpio, level, tick):
	global waveTick,slash,ppm,onetwo
	wavelength=1000000
	waveTick=tick
	offset=(pigpio.tickDiff(RTCtick,waveTick) % wavelength)
	print "-"
	if offset >=600000:
		offset=(offset-wavelength)
	if onetwo:
		slash=offset
	else:
		slash=0
	onetwo=not onetwo
	print "Slash:",offset,slash,ticks2unixUTC(tick),ppm
	#print "WaveTick",waveTick
	#checkWaveBuffer()
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
	# 
	if not pi.wave_tx_busy():
		sendWave()	
		print "WAVE END!!"



#corrected RTCsecond,RTCtick and ppm 
def ticks2unixUTC(tick):
	global RTCsecond,RTCtick,ppm
	tickOffset=pigpio.tickDiff(RTCtick, tick)
	#print RTCsecond,RTCtick,tick,tickOffset
	bias=ppm*(tickOffset/1000000.)
	UTC=float(RTCsecond)+(tickOffset+bias)/1000000.
	#print (RTCsecond,ppm,tick,tickOffset,bias,UTC)
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
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:%s" % zmqTripPort)
	getSystemClockData()
	pi.wave_clear()
	pi.set_mode(TRIP_WAVE_REF_GPIO,pigpio.OUTPUT)
	pi.set_mode(TRIP_GPIO,pigpio.OUTPUT)
	#pi.set_pull_up_down(TRIP_WAVE_REF_GPIO, pigpio.PUD_DOWN)
	#pi.set_pull_up_down(PPS_GPIO, pigpio.PUD_DOWN)
	#pi.set_pull_up_down(TRIP_GPIO, pigpio.PUD_DOWN)
	#print pi.get_mode(TRIP_WAVE_REF_GPIO), pi.get_mode(TRIP_GPIO), pi.get_mode(PPS_GPIO)
	cb1 = pi.callback(TRIP_WAVE_REF_GPIO, pigpio.RISING_EDGE, getWaveTick)
	cb2 = pi.callback(PPS_GPIO, pigpio.RISING_EDGE, discipline)
	sendWave()
	now=time.time()
	RTCtrip=int(round(now))+10.001
	while True:
	    	#  Wait for next request from client
	    	message = socket.recv()
		RTCtrip	=float(message)
		print RTCtrip,"Trip set: %s" %  unixTime2date(RTCtrip)
		time.sleep(0.1)
		#  Send reply back to client
		socket.send(unixTime2date(RTCtrip))


