#!/bin/bash
rm client.dat server.dat 
export PYTHONUNBUFFERED=yes
../zmqClientForTest.py > client.dat &
ssh  pi@nachoplus-rpi 'sudo /home/pi/gpio/wiringPI/server' >server.dat
killall zmqClientForTest.py
