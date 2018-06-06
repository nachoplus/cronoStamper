#!/usr/bin/python
'''
Trip a preprogramed trigger signal
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
RTCtripList=[]

ppm=0
pllOffset=0
lastHIGH=0
lastLOW=0

onetwo=True

pi=pigpio.pi()

def trip():
	global RTCtripList,RTCsecond,RTCtrip
	if len(RTCtripList)==0:
		return False
	try:
		while RTCtripList[0]<=ticks2unixUTC(waveTick)+1:
			RTCtripList.remove(RTCtripList[0])
	except:
		print "Trip list empty"
	if len(RTCtripList)==0:
		return False
	RTCtrip=RTCtripList[0]
	delta=RTCtrip-ticks2unixUTC(waveTick)
	if delta>=1. and delta<2. :
		print "RTC:",RTCtrip,RTCsecond,delta
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
	global RTCsecond,RTCtick,ppm,lastSecondTicks,slash,pllOffset
	pulse=100000
	wavelength=1000000-ppm
	preamble=0
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
	global waveTick,slash,ppm,onetwo,pllOffset
	wavelength=1000000-ppm
	waveTick=tick
	offset=(pigpio.tickDiff(RTCtick,waveTick) % wavelength)
	print "-"
	if offset >=600000:
		offset=(offset-wavelength)
	if onetwo:
		slash=round(offset)
	else:
		slash=0
	onetwo=not onetwo
	print "Slash:",ppm,slash,ticks2unixUTC(tick),round(offset)
	#print "WaveTick",waveTick
	#checkWaveBuffer()
	sendWave()

#get the PLL system clock correction in PPM
def getPPM():
	global ppm,pllOffset
	clkData=getSystemClockData()
       	ppm=float(clkData['ppm'])
    	pllOffset=float(clkData['pllOffset'])

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

def ticks2unixUTC(tick):
	global RTCsecond,RTCtick,ppm
	tickOffset=pigpio.tickDiff(RTCtick, tick)
	#print RTCsecond,RTCtick,tick,tickOffset
	bias=ppm*(tickOffset/1000000.)
	UTC=float(RTCsecond)+(tickOffset+bias)/1000000.
	#print (RTCsecond,ppm,tick,tickOffset,bias,UTC)
	return UTC

def unixTime2date(unixtime):
	d = str(datetime.datetime.fromtimestamp(unixtime))
	return d

def unixTime2MJD(unixtime):
	return ( unixtime / 86400.0 ) + 2440587.5 - 2400000.5

class cmdProcesor:
	def __init__(self):
		self.CMDs={ 
		"UNIXTIME": self.cmd_alarmUnixTime,  \
  		"MJD": self.cmd_alarmMJD,  \
  		"DATE": self.cmd_alarmDate,  \
  		"CLEAR": self.cmd_clearAlarms,  \
  		"LIST": self.cmd_listAlarms,  \
  		"help": self.cmd_help, \
  		"?": self.cmd_help
		}

	def cmd(self,cmd):
                for c in self.CMDs.keys():
			l=len(c)
			if (cmd[:l]==c):
				arg=cmd[l:].strip()
				return self.CMDs[c](arg)
				break
		error="ERROR. Command not implemented:",cmd
		return error

	def cmd_help(self,arg):
		response='\n'.join(self.CMDs.keys())
		return "OK. Available commands:\n"+response

	def alarm_str(self,unixtime):
		response=str(unixTime2date(unixtime))+" UNIX:"+str(unixtime)+" MJD:"+str(unixTime2MJD(unixtime))
		return response

	def set_alarm(self,unixtime):
		RTCtripList.append(unixtime)
		RTCtripList.sort()
		response=self.alarm_str(unixtime)
		return "OK. New alarm:"+response

	def cmd_alarmUnixTime(self,arg):
		global RTCtripList 
		c=arg.split()
		time=c[0]
		return self.set_alarm(float(time))

	def cmd_alarmMJD(self,arg):
		c=arg.split()
		mjdtime=float(c[0])
		unixtime=(mjd - 2440587.5 + 2400000.5)*86400.0
		return self.set_alarm(unixtime)

	def cmd_alarmDate(self,arg):
		try:
			date = datetime.datetime.strptime(arg, '%Y-%m-%d %H:%M:%S.%f')
		except:
			return "ERROR. Bad date. Expected format '%Y-%m-%d %H:%M:%S.%f'"
		#mktime FAIL TO get microseconds
		unixtime = time.mktime(date.timetuple())
		print date,unixtime
		return self.set_alarm(unixtime)

	def cmd_listAlarms(self,arg):
		global RTCtripList
		d=[]
		for a in RTCtripList:
			response=self.alarm_str(a)
			d.append(response)
		response='\n'.join(d)
		return "OK.Alarm list:\n"+response

	def cmd_clearAlarms(self,arg):
		global RTCtripList
		RTCtripList=[]
		return "OK. All alarms cleared."


if __name__ == '__main__':
	processor=cmdProcesor()
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:%s" % zmqTripPort)
	getSystemClockData()
	pi.wave_clear()
	pi.set_mode(TRIP_WAVE_REF_GPIO,pigpio.OUTPUT)
	pi.set_mode(TRIP_GPIO,pigpio.OUTPUT)
	cb1 = pi.callback(TRIP_WAVE_REF_GPIO, pigpio.RISING_EDGE, getWaveTick)
	cb2 = pi.callback(PPS_GPIO, pigpio.RISING_EDGE, discipline)
	sendWave()

	while True:
	    	#  Wait for next request from client
	    	message = socket.recv()
		print "CMD:",message
		response=processor.cmd(message)
		socket.send(response)
		time.sleep(0.01)


