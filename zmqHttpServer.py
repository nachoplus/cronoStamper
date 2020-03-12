#!/usr/bin/python
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
    return render_template('help.html')

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
		deep='200'
	os.environ["_CLK_SAMPLES"] = deep
	getpeersCMD="ntpq -np|grep '+'"
	peers=commands.getstatusoutput(getpeersCMD)
	peers=peers[1].split('\n')
	npeers=len(peers)
	print npeers,peers
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
	exe=path+'/test/peerGraph.plot  >'+path+'/test/clockStats.png'
	cmdrst=commands.getstatusoutput(exe)
	return send_from_directory(directory=path+'/test', filename='clockStats.png')

@app.route('/trigger.json')
def trigger():
    zmqSocket = context.socket(zmq.REQ)
    zmqSocket.connect("tcp://localhost:%s" % zmqTripPort)
    zmqSocket.send('NEXT')
    reply=zmqSocket.recv()
    zmqSocket.close()
    r={'nextTrip':reply}
    return jsonify(r)


def lastValue():
	global last
	try:
		m= socket.recv(flags=zmq.NOBLOCK)
		topic, msg  = demogrify(m)
		#print "Set:",last
		last=msg
	except:
		#print "Get:",last
		msg=last
    	return msg

def lastGPSValue():
        from time import gmtime, strftime
        time=strftime("%H:%M:%S +0000", gmtime())
	global lastGPS
	try:
		m= socketGPS.recv(flags=zmq.NOBLOCK)
		topic, msg  = demogrify(m)
		#print "Set:",last
		lastGPS=msg
	except:
		#print "Get:",last
		msg=lastGPS
        finally:
                msg['clktime']=time
    	return msg


if __name__ == '__main__':
	context = zmq.Context()
	topicfilter = ShutterFlange
	socket = context.socket(zmq.SUB)
	#CONFLATE: get only one message (do not work with the stock version of zmq, works from ver 4.1.4)
	socket.setsockopt(zmq.CONFLATE, 1)
	socket.connect ("tcp://localhost:%s" % zmqShutterPort)
	socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

	topicfilter = "GPS"
	socketGPS = context.socket(zmq.SUB)
	#CONFLATE: get only one message (do not work with the stock version of zmq, works from ver 4.1.4)
	socketGPS.setsockopt(zmq.CONFLATE, 1)
	socketGPS.connect ("tcp://localhost:%s" % zmqGPSPort)
	socketGPS.setsockopt(zmq.SUBSCRIBE, topicfilter)


	#main loop
	app.run(host='0.0.0.0',port=httpPort,debug=True)

