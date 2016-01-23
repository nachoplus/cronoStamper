#!/bin/bash
rm client.dat server.dat clock.dat
export PYTHONUNBUFFERED=yes
ssh  pi@nachoplus-rpi 'echo "nachoplus-rpi clock info";ntpq -p;echo "";ntpdc -c kerninfo' >clock.dat
echo "" >> clock.dat
ssh  pi@192.168.1.36 'echo "cronoStamper clock info";ntpq -p;echo "";ntpdc -c kerninfo' >>clock.dat
../zmqClient.py > client.dat &
ssh  pi@nachoplus-rpi 'sudo /home/pi/gpio/wiringPI/server' >server.dat

