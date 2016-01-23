__CronoStamper__
========

Introduction
------------

High precisión timestamping.

Nacho Mas - January 2016

__Installing__
----------


first get minibian from https://minibianpi.wordpress.com/download/
and make and SD as raspberry usual

boot the raspberry log as root and run the following commands:

#Basic packages
apt-get update
apt-get dist-upgrade
raspi-config
 ---> Expand Filesystem  -> //Do it

apt-get install nano apt-utils bash-completion rpi-update raspi-config unzip make gcc
rpi-update 
reboot

#Setup high precisón GPS-PPS disciplined clock
More information on: http://www.satsignal.eu/ntp/Raspberry-Pi-quickstart.html

*disable serial console:
 sudo raspi-config
 ---> Advanced Options -> Disable Serial Shell (optional) 
 .....

*Edit some files
nano /boot/config.txt - Add dtoverlay=pps-gpio,gpiopin=18 on a new line
nano /etc/modules – Add pps-gpio on a new line, if it is not already present.

apt-get install pps-tools
apt-get install libcap-dev
apt-get install gpsd ntp


# Setup cronostamper specific
get pigpiod and compile
wget abyz.co.uk/rpi/pigpio/pigpio.zip
unzip pigpio.zip
cd PIGPIO
make
sudo make install



FLASK for the embebeded web server
sudo apt-get install python-flask python-dev

mkdir SDKs
mkdir zmq
chmod zmq
Get zmq lastes. If not CONFLATE does not work
wget http://download.zeromq.org/zeromq-3.2.5.tar.gz
