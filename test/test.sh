#!/bin/bash
rm client.dat server.dat 
export PYTHONUNBUFFERED=yes
../zmqClient.py > client.dat &
ssh  pi@nachoplus-rpi 'sudo /home/pi/gpio/wiringPI/server' >server.dat
cat test.R |R --vanilla
killall zmqClientForTest.py
