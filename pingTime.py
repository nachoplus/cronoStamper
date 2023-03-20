#!/usr/bin/python3
'''
Pingtime. Return the timestamp of
a newly open connection.

Nacho Mas January-2017
'''
import socket
import sys
import time
import datetime
import threading
from config import *
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = pingPort # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logging.info('Starting CronoStamper ping Time.')
logging.info('Socket created')
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    logging.error(f'Bind failed. Error Code : {msg[0]} Message {msg[1]}')
    sys.exit()
     
logging.info(f'binded to {HOST}:{PORT}')
 
#Start listening on socket
s.listen(10)
logging.info('Socket now listening')
 

def clientthread(conn,addr):
    logging.info( f'Connected with {addr[0]}:{addr[1]}')
    d = str(datetime.datetime.now())
    conn.sendall(f'{d}\r\n'.encode())
    logging.info( f'Sent {d} to {addr[0]}:{addr[1]}. Disconnecting')    
    conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    t = threading.Thread(target=clientthread,args=(conn,addr,))
    t.start()

s.close()
