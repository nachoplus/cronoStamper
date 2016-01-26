#!/usr/bin/python
'''
    Simple CCD tregger simulator. Open a socket and execute
    ./oneShot when someone get connected and exit.
    Nacho Mas January 2016
'''

import socket
import commands
from thread import *
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 7777 # Arbitrary non-privileged port
 
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
 

def clientthread(conn):
	rst=commands.getoutput('./oneShot')
        print rst
	conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
 
s.close()
