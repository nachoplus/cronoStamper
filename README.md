__CronoStamper__
========
Introduction
------------
TBD

__Installing__
----------
#NACHO MAS - January 2016
#
#first get minibian from https://minibianpi.wordpress.com/download/
# and make and SD with dd 
#
#boot the raspberry and run the following commands:
#BASIC
apt-get update
apt-get dist-upgrade
# sudo raspi-config
# 1. Expand Filesystem  -> //Do it

apt-get install nano apt-utils bash-completion rpi-update raspi-config unzip make gcc
rpi-update 
reboot

#setup time related
#http://www.satsignal.eu/ntp/Raspberry-Pi-NTP.html
# o better: http://www.satsignal.eu/ntp/Raspberry-Pi-quickstart.html
#
# disable serial console:
# sudo raspi-config
# 1. Expand Filesystem 
# 2. Advanced Options -> Disable Serial Shell (optional) 
# .....
# Edit some files
# nano /boot/config.txt - Add dtoverlay=pps-gpio,gpiopin=18 on a new line
# sudo nano /etc/modules – Add pps-gpio on a new line, if it is not already present.
apt-get install pps-tools
apt-get install libcap-dev
apt-get install gpsd ntp


#cronostamper specific
#get pigpiod and compile
wget abyz.co.uk/rpi/pigpio/pigpio.zip
unzip pigpio.zip
cd PIGPIO
make
sudo make install

#

#FLASK for the embebeded web server
sudo apt-get install python-flask python-dev

mkdir SDKs
mkdir zmq
chmod zmq
#Get zmq lastes. If not CONFLATE does not work
wget http://download.zeromq.org/zeromq-3.2.5.tar.gz
