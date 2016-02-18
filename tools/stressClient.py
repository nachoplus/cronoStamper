#!/usr/bin/python
'''
    Simple CCD tregger simulator. Open a socket and execute
    ./oneShot when someone get connected and exit.
    Nacho Mas January 2016
'''

import socket
import commands
import time
import sys
from thread import *
 
HOST = 'cronostamper'   # Symbolic name meaning all available interfaces
PORT = 9999 # Arbitrary non-privileged port
 
print 'Starting CronoStamper Sockets Stress Client.'

i=0
#now keep talking with the server
while True:
	i=i+1
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = (HOST, PORT)
	print 'New connection',i
	print >>sys.stderr, 'connecting to %s port %s' % server_address
	sock.connect(server_address)
	for j in range(0,5):
		msg=sock.recv(1024)
		print i*j,i,j,msg,
	sock.close()
	time.sleep(2)
