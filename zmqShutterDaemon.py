#!/usr/bin/python

import pigpio
import time
import datetime
import zmq
import commands
import json

from config import *


RTCsecond=0
RTCtick=0
ppm=0
pllOffset=0

lastHIGH=0
lastLOW=0

pi=pigpio.pi()



#get the PLL system clock correction in PPM
def getPPM():
	global ppm,pllOffset
	clkData=getSystemClockData()
       	ppm=float(clkData['ppm'])
	pllOffset=float(clkData['pllOffset'])




#get data to correlate system time with the CPU ticks
#use PPS signal interrupt to get tick:UTCtime point
def discipline(gpio, level, tick):
	global RTCsecond,RTCtick
	now=time.time()
	getPPM()
	RTCsecond=int(round(now))
	RTCtick=tick
	#print (now,RTCsecond,ppm,pllOffset,RTCtick)
	

#corrected RTCsecond,RTCtick and ppm 
def ticks2unixUTC(tick):
	global RTCsecond,RTCtick,ppm,pllOffset
	tickOffset=pigpio.tickDiff(RTCtick, tick)
	bias=ppm*(tickOffset/1000000.)
	UTC=float(RTCsecond)+(tickOffset+bias)/1000000.
	#print (RTCsecond,ppm,tick,tickOffset,pllOffset,bias,UTC)
	return UTC

#get UTC timestamp for the incoming pulse
def GPIOshutter(gpio, level, tick):
	global lastHIGH,lastLOW
	unixUTC=ticks2unixUTC(tick)
	dateUTC=unixTime2date(unixUTC)
	MJD=unixTime2MJD(unixUTC)
	if level == 1:
		topic="SHUTTER_HIGH"
		lastHIGH=unixUTC
		pulse=unixUTC-lastLOW
	else:
		topic="SHUTTER_LOW"
		lastLOW=unixUTC
		pulse=unixUTC-lastHIGH
	msg = {'tick':tick,'level':level,'unixUTC':unixUTC,'dateUTC':dateUTC,'MJD':MJD,'pulse':pulse}
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
	socket.bind("tcp://*:%s" % zmqPort)
	getSystemClockData()
	cb1 = pi.callback(11, pigpio.EITHER_EDGE, GPIOshutter)
	cb2 = pi.callback(18, pigpio.RISING_EDGE, discipline)
	while True:
	    time.sleep(1)


