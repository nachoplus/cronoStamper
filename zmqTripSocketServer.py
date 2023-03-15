#!/usr/bin/python3
'''
TRIP Sockets server- 
On connect send a string with the 
timestamp of the last high SIGNAL.
Then close the sockets

Nacho Mas june-2018
'''

import socket
import sys
import select
import time
#from thread import *
import threading
import zmq
from config import *


context = zmq.Context()

 
HOST = ''   # Symbolic name meaning all available interfaces
 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logging.info('Starting Trip TCP server')

#Bind socket to local host and port
try:
    s.bind((HOST, TripPort))
    logging.info(f'Socket created {HOST}:{TripPort}')    
except socket.error as msg:
    logging.error(f'Bind failed. Error Code :{msg[0]} Message {msg[1]}')
    sys.exit()
     
logging.info('Socket bind completed')
 
#Start listening on socket
s.listen(1)
logging.info('Socket now listening')
 


#End='something useable as an end marker'
def recv_end(conn):
    End='#'
    total_data=[]
    while True:
        time.sleep(0.05)
        data=''
        try:	
            data=conn.recv(1).decode()
        except:
            logging.warning("socket close")
            cmd="SOCKET_CLOSE"	
            break
        if data=='':
            cmd="SOCKET_CLOSE"	
            break

        if End in data:
            total_data.append(data[:data.find(End)])
            cmd=''.join(total_data).replace('\n','').replace('\r','')
            if len(cmd)==0:
                continue
            else:
                break
        else:
            total_data.append(data)

    #print ("CMD parse:",repr(cmd))
    return cmd

#Function for handling connections. This will be used to create threads
def clientthread(conn):
    RUN=True
    #  Socket to talk to ZMQserver
    zmqSocket = context.socket(zmq.REQ)
    zmqSocket.REQ_CORRELATE=True
    zmqSocket.REQ_RELAXED= True
    zmqSocket.RCVTIMEO=200
    zmq_trip_endpoint=f"tcp://localhost:{zmqTripPort}"
    logging.info(f'Subscribed to TRIP zmq_endpoint:{zmq_trip_endpoint}')
    zmqSocket.connect(zmq_trip_endpoint)

    #infinite loop so that function do not terminate and thread do not end.
    while RUN:
        try:
            cmd=recv_end(conn)
            if cmd == "SOCKET_CLOSE" or cmd == "EXIT" or cmd == "QUIT":
                break
            print ("<-",cmd)
            zmqSocket.send_string(cmd)
            reply=zmqSocket.recv_string()
            print ("->",reply)
            conn.send(f'{reply}\n'.encode())
        except:
            conn.send(f'TRIP DAEMON FAIL\n'.encode())
            logging.error(f'TRIP DAEMON FAIL\n')

    #came out of loop
    #conn.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
    conn.close()
    logging.warning("Disconnecting..")
 
#now keep talking with the client
RUN=True
while RUN:
  try:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    logging.info(f'Connected with {addr[0]}:{addr[1]}')
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    #start_new_thread(clientthread ,(conn,))
    t = threading.Thread(target=clientthread,args=(conn,))
    t.start()
  except:
    RUN=False
	
s.close()

