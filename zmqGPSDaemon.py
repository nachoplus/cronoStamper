#! /usr/bin/python3
'''
Get data from GPSD to know if GPS subsyste is working ok.

Base on the work of Dan Mandle http://dan.mandle.me September 2012

Nacho Mas Junary-2017
'''
 
import os
import gps
import time
import threading
import time
import datetime
import zmq
import json

from config import *




class gps2zmq:
	def __init__(self):
		self.datakeys=()	
		self.gpsdConnect()

	def gpsdConnect(self):
		try:
			flags= gps.WATCH_ENABLE | gps.WATCH_PPS 
			self.session = gps.gps(mode=flags)	
			print("GPSD contacted")
		except:
			print("GPSD not running. Retrying..")

	def run(self):
		while True:
			clk=getSystemClockData()
			fix=dict(clk)
			try:
				# Do stuff
				report = self.session.next()
				if report['class'] == 'TPV':
					# Do more stuff
					fix.update(report)
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
						nsat={'nsat':f'{str(uses)}/{str(len(sats))}','satellites':sats}
						fix.update(nsat)					
					'''
					status={'gpsStatus':'OK'}
					fix.update(status)
					self.datakeys=fix.keys()
					print(fix)
					socket.send(mogrify('GPS',fix))

			except:
				for key in self.datakeys:
					fix.update({key:'-'})		
				fix.update(clk)
				fix.update({'gpsStatus':'FAIL'})
				fix.update({'mode':'GPSD FAIL'})	
				print(fix)
				socket.send(mogrify('GPS',fix))
				self.gpsdConnect()
				time.sleep(1)
			
		


 
if __name__ == '__main__':
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:%s" % zmqGPSPort)
	poller=gps2zmq()
	poller.run()

