#!/usr/bin/python
#NACHO MAS mas.ignacio@gmail.com
#January 2015
#
# Not used in the actual suite

#This script read ntpd logs endlessly and 
#write a json file with selected information
#to be consume by ajax pages. The final aim is 
#to show if UTC time is ok

import time
import numpy as np
#from collections import deque

class ntpMonitor:
	#Location of ntpd stats files
        loopstats='/var/log/ntpstats/loopstats'
        peerstats='/var/log/ntpstats/peerstats'
	#show only de last seconds
        showSeconds=1
	bufferDeep=40
	dt=np.dtype([('MJD', 'f4'),('peer', 'S10'), ('status', 'S10'), \
 		  ('offset', 'f4'),('delay', 'f4'), ('dispersion', 'f4'), \
		  ('jitter', 'f4')])

	data=np.array(np.zeros(bufferDeep),dtype=dt)
	indx=0	

	def __init__(self):
		pass

	def run(self):
	    	logfile = open(self.peerstats,"r")
		for line in logfile:
			d=line.split()
			self.data[self.indx]['MJD']=d[1]
			self.data[self.indx]['peer']=d[2]
			self.data[self.indx]['status']=d[3]
			self.data[self.indx]['offset']=float(d[4])
			self.data[self.indx]['delay']=float(d[5])
			self.data[self.indx]['dispersion']=float(d[5])
			self.data[self.indx]['jitter']=float(d[7])
			self.indx=self.indx+1
			if   self.indx>=self.bufferDeep:
				self.indx=0

		print self.data

		loglines = self.follow(logfile)
    		for line in loglines:
			d=line.split()
			print d
			self.data[self.indx]['MJD']=d[1]
			self.data[self.indx]['peer']=d[2]
			self.data[self.indx]['status']=d[3]
			self.data[self.indx]['offset']=float(d[4])
			self.data[self.indx]['delay']=float(d[5])
			self.data[self.indx]['dispersion']=float(d[5])
			self.data[self.indx]['jitter']=float(d[7])
			self.indx=self.indx+1
			if   self.indx>=self.bufferDeep:
				self.indx=0
			self.update()

        def update(self):
		print self.data
		print "--"
		pass

	def follow(self,thefile):
	    thefile.seek(0,2)
	    while True:
	        line = thefile.readline()
	        if not line:
	            time.sleep(0.1)
	            continue
	        yield line

if __name__ == '__main__':
	mon=ntpMonitor()
	mon.run()
