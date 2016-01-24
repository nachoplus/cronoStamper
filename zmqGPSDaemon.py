#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
 
import os
import gps
import time
import threading
import time
import datetime
import zmq
import commands
import json

from config import *




class gps2zmq:
     def __init__(self):
	flags= gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE 
	self.session = gps.gps(mode=flags)	
	self.datakeys=()
     def run(self):
	try:
	    while True:
	        # Do stuff
	        report = self.session.next()
	        if report['class'] == 'TPV':
		        # Do more stuff
			clk=self.getSystemClockData()
			fix=dict(report)
	     		fix.update(clk)
			#print fix
			'''
			while report['class'] != 'SKY':
 		        	report = self.session.next()
			if 'satellites' in report:
				sats=report['satellites']
				sats=map( lambda x : dict(x) , sats )
				uses=0
				for sat in sats:
					if sat['used']:
						uses=uses+1
				nsat={'nsat':str(uses)+'/'+str(len(sats)),'satellites':sats}
				fix.update(nsat)
				self.datakeys=fix.keys()
			'''
			socket.send(mogrify('GPS',fix))

	except StopIteration:
	    msg={}	
            for key in self.datakeys:
		 msg.update({key:'-'})		
  	    socket.send(mogrify('GPS',msg))
	    print "GPSD has terminated"
	


     def getSystemClockData(self):
	rst=commands.getoutput('ntpq -c kern')
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

	msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error}
	return msg

 
if __name__ == '__main__':
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:%s" % zmqGPSPort)
	poller=gps2zmq()
	poller.run()

