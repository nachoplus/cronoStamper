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

			while report['class'] != 'SKY':
 		        	report = self.session.next()
			sats=report['satellites']
			sats=map( lambda x : dict(x) , sats )
			uses=0
			for sat in sats:
				if sat['used']:
					uses=uses+1
			nsat={'nsat':str(uses)+'/'+str(len(sats)),'satellites':sats}
			fix.update(nsat)
			self.datakeys=fix.keys()
			#print self.datakeys
			socket.send(mogrify('GPS',fix))
	except StopIteration:
	    msg={}	
            for key in self.datakeys:
		 msg.update({key:'-'})		
  	    socket.send(mogrify('GPS',msg))
	    print "GPSD has terminated"
	


     def getSystemClockData(self):

		rst=commands.getoutput('ntpq -c kern')
		out=rst.split()
	        ppm=float(out[5])
		pllOffset=float(out[2])
	        maxError=float(out[8])
		Error=float(out[11])

		msg={'pllOffset':pllOffset,'ppm':ppm,'ClkMaxError':maxError,'ClkError':Error}
		return msg

 
if __name__ == '__main__':
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:%s" % zmqGPSPort)
	poller=gps2zmq()
	poller.run()

