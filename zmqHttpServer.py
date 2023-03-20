#!/usr/bin/python3
'''
HTTP server
Show several stats and has a littel url interface:

/dateUTC return the UTC timestamp of the last SIGNAL

Nacho Mas January-2017
'''

from flask import Flask, render_template, request, jsonify,send_from_directory
from functools import wraps, update_wrapper
import zmq
import time
import os
from config import *

app = Flask(__name__)
last={}
lastGPS={}


@app.route('/')
def index():
    return render_template('cronoStamper.html', camera=camera)

@app.route('/help')
def help():
    return render_template('help.html',ports=ports)

@app.route('/clock.json')
def clock():
	from time import gmtime, strftime
	time=strftime("%Y-%m-%d %H:%M:%S", gmtime())
	msg=getSystemClockData()
	msg['clktime']=time
	return msg

@app.route('/gps.json')
def gps_json():
	return jsonify(lastGPSValue())

@app.route('/shutter.json')
def shutter_json():
	return jsonify(lastValue())


@app.route('/unixUTC')
def unixUTC():
	return "%f" % lastValue()['unixUTC']

@app.route('/dateUTC')
def dateUTC():
	return "%s" % lastValue()['dateUTC']

@app.route('/MJD')
def MJD():
	return "%0.12f" % lastValue()['MJD']

@app.route('/gps_chart')
def gps_chart():
    return render_template('clock_chart.html')

@app.route('/clkStatus')
def clkStatus():
	deep=request.args.get('deep')
	if deep==None:
		deep='60'
	os.environ["_CLK_SAMPLES"] = deep
	#getpeersCMD="chronyc -n sources|grep '^\^'"
	getpeersCMD='cat  /var/log/chrony/measurements.log |grep -v "PPS"|grep -v "GPS"|grep -v "UTC"|grep -v "="|tr -s " "|cut -d" " -f 3|tail -2'
	peers=getstatusoutput(getpeersCMD)
	peers=peers[1].decode().split('\n')
	npeers=len(peers)
	logging.debug(f'{npeers} peers:{peers}')	
	os.environ["_NTP_INTERNET_PEER0"] = 'kkk'
	os.environ["_NTP_INTERNET_PEER1"] = 'kkk'
	if npeers>=1:
		os.environ["_NTP_INTERNET_PEER0"] = peers[0]
	if npeers>=2:
		os.environ["_NTP_INTERNET_PEER1"] = peers[1]
	path=os.path.dirname(os.path.realpath(__file__))
	exe=path+'/test/peerGraph.plot  >'+path+'/test/clockStats.png'
	cmdrst=getstatusoutput(exe)
	return send_from_directory(directory=path+'/test', path='clockStats.png')    

@app.route('/clkStatus_ntpd')
def clkStatus_ntpd():
	deep=request.args.get('deep')
	if deep==None:
		deep='200'
	os.environ["_CLK_SAMPLES"] = deep
	getpeersCMD="ntpq -np|grep '^+'"
	peers=getstatusoutput(getpeersCMD)
	peers=peers[1].split('\n')
	npeers=len(peers)
	logging.debug(f'{npeers} peers:{peers}')	
	os.environ["_NTP_INTERNET_PEER0"] = 'kkk'
	os.environ["_NTP_INTERNET_PEER1"] = 'kkk'
	if npeers>=1:
		if len(peers[0])>10:
			peer=peers[0].split()[0][1:]
			os.environ["_NTP_INTERNET_PEER0"] = peer
	if npeers>=2:
		peer=peers[1].split()[0][1:]
		os.environ["_NTP_INTERNET_PEER1"] = peer
	path=os.path.dirname(os.path.realpath(__file__))
	exe=path+'/test/peerGraph_ntpd.plot  >'+path+'/test/clockStats_ntpd.png'
	cmdrst=getstatusoutput(exe)
	return send_from_directory(directory=path+'/test', filename='clockStats_ntpd.png', cache_timeout= 0)

@app.route('/trigger.json')
def trigger():
	try:
		triggerSocket.send_string('NEXT')
		reply=triggerSocket.recv_string()
		triggerOK=True
	except:
		reply="TRIGGER DAEMON FAIL"
		triggerOK=False
	r={'nextTrip':reply,'triggerOK':triggerOK}
	logging.debug(f'{r}')	
	return jsonify(r)


def lastValue():
	global last
	try:
		m= socket.recv(flags=zmq.NOBLOCK)
		topic, msg  = demogrify(m)
		last=msg
	except:
		msg=last

	return msg

def lastGPSValue():
	global lastGPS
	try:
		m= socketGPS.recv(flags=zmq.NOBLOCK)
		topic, msg  = demogrify(m)
		lastGPS=msg
	except:
		msg=lastGPS

	return msg


if __name__ == '__main__':
	context = zmq.Context()
	topicfilter = ShutterFlange
	socket = context.socket(zmq.SUB)
	#CONFLATE: get only one message (do not work with the stock version of zmq, works from ver 4.1.4)
	zmq_shutter_endpoint=f"tcp://localhost:{zmqShutterPort}"
	logging.info(f'Subscribed to Shutter zmq_endpoint:{zmq_shutter_endpoint} topic:{topicfilter} CONFLATE')
	socket.setsockopt(zmq.CONFLATE, 1)
	socket.connect (zmq_shutter_endpoint)
	socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

	GPStopicfilter = "GPS"
	zmq_gps_endpoint=f"tcp://localhost:{zmqGPSPort}"	
	logging.info(f'Subscribed to GPS zmq_endpoint:{zmq_gps_endpoint} topic:{GPStopicfilter} CONFLATE')		
	socketGPS = context.socket(zmq.SUB)
	#CONFLATE: get only one message (do not work with the stock version of zmq, works from ver 4.1.4)
	socketGPS.setsockopt(zmq.CONFLATE, 1)
	socketGPS.connect (zmq_gps_endpoint)
	socketGPS.setsockopt_string(zmq.SUBSCRIBE, GPStopicfilter)
	triggerSocket = context.socket(zmq.REQ)
	triggerSocket.REQ_CORRELATE=True
	triggerSocket.REQ_RELAXED= True
	triggerSocket.RCVTIMEO=200
	zmq_trigger_endpoint=f"tcp://localhost:{zmqTriggerPort}"
	logging.info(f'Subscribed to TRIGGER zmq_endpoint:{zmq_trigger_endpoint}')
	triggerSocket.connect(zmq_trigger_endpoint)

	#main loop
	app.run(host='0.0.0.0',port=httpPort,debug=False)

