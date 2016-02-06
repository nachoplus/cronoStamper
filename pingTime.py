#!/usr/bin/python
'''
    Simple socket server using threads
'''

import socket
import commands
import sys
import time
import datetime
import threading
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 7777 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Starting CronoStamper ping Time.'
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
 

def clientthread(conn,addr):
	print 'Connected with ' + addr[0] + ':' + str(addr[1])
        d = str(datetime.datetime.now())
	conn.sendall(d+'\r\n')
        print d
	conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()

     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    t = threading.Thread(target=clientthread,args=(conn,addr,))
    t.start()

s.close()
