#!/usr/bin/python
'''
    Check pingTime daemon
    Nacho Mas January 2016
'''

import socket
import time
import datetime

 
HOST = 'cronostamper'   # Symbolic name meaning all available interfaces
PORT = 5555 # Arbitrary non-privileged port
 


i=0
#now keep talking with the server
while True:
	i=i+1
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = (HOST, PORT)
	d=str(datetime.datetime.utcnow())
	sock.connect(server_address)
	msg=sock.recv(1024)
	dd=d.split()[1].split(":")
	dmsg=msg.split()[1].split(":")
	sd=float(dd[2])+float(dd[1])*60
	smsg=float(dmsg[2])+float(dmsg[1])*60
	print sd,smsg
	sock.close()
	time.sleep(0.01)

