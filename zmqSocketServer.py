#!/usr/bin/python
'''
    Simple socket server using threads
'''

import zmq
import time
import socket
import sys
from thread import *
from config import *
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = socketsPort # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Starting CronoStamper Sockets Server.'
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Socket now listening'
 


#Function for handling connections. This will be used to create threads
def clientthread(conn):

    context = zmq.Context()
    topicfilter = "SHUTTER_HIGH"
    socket = context.socket(zmq.SUB)
    #only one message (do not work with the stock version of zmq, works from ver 4.1.4)
    socket.setsockopt(zmq.CONFLATE, 1)
    socket.connect ("tcp://localhost:%s" % zmqPort)
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

    #Sending message to connected client
    #conn.send('OK.CronoStamper socket server.\n') #send only takes string
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
	        #Receiving from client
	        #data = conn.recv(1024)
		m= socket.recv()
		topic, msg  = demogrify(m)
		reply = msg['dateUTC']+'\n'
    		conn.sendall(reply)
     
    #came out of loop
    conn.close()
 
#now keep talking with the client
while True:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
 
s.close()
