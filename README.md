__CronoStamper__
========

Introduction
------------

High precisión timestamping.

Nacho Mas - January 2016

__Installing__
----------


First get minibian from https://minibianpi.wordpress.com/download/
and make and SD as raspberry usual

boot the raspberry log as root and run the following commands:

#Basic packages
>apt-get update

>apt-get dist-upgrade

>raspi-config

> ---> Expand Filesystem  -> //Do it

>apt-get install nano apt-utils bash-completion rpi-update raspi-config unzip make gcc

>apt-get install minicom git

>rpi-update 

>reboot

#Setup high precisón GPS-PPS disciplined clock
More information on: http://www.satsignal.eu/ntp/Raspberry-Pi-quickstart.html

disable serial console:
>raspi-config

>---> Advanced Options -> Disable Serial Shell (optional) 

>.....

Edit some files

>nano /boot/cmdline.txt

(remove the two parameters including the string "ttyAMA0": console=ttyAMA0,115200 kgdboc=ttyAMA0,115200)

>nano /etc/inittab

(Comment out the line like "2:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100"  by putting a hash (#) at the start of the line.  Note that the line was not  2:23 on my version of Linux, so be sure to look for the actual line with ttyAMA0.  It was the last line of the file, as it happens).

>nano /boot/config.txt 

Add dtoverlay=pps-gpio,gpiopin=18 on a new line

>nano /etc/modules 

Add pps-gpio on a new line, if it is not already present.

>nano /etc/default/gpsd

Set GPSD_OPTIONS="-n" and DEVICE='/dev/ttyAMA0'

>reboot

>apt-get install pps-tools

>apt-get install libcap-dev

>apt-get install gpsd gpsd-clients ntp

The supplied version of NTPD on the Raspberry Pi doesn’t support PPS so we need to recompile it (Please note that the configure and compile steps may take up to 30 minutes). 

Check last version from http://www.ntp.org/downloads.html

>wget http://archive.ntp.org/ntp4/ntp-4.2.8p6.tar.gz

>tar zxvf ntp-4.2.8p6.tar.gz 

>cd ntp-4.2.8p6

>./configure

>make

>make install

>service ntp stop

>/usr/local/bin/ntp* /usr/bin/ && sudo cp /usr/local/sbin/ntp* /usr/sbin/

>nano /etc/ntp.conf 


# Setup cronostamper specific

Get the pigpiod daemon http://abyz.co.uk/rpi/pigpio/index.html and compile

>wget abyz.co.uk/rpi/pigpio/pigpio.zip

>unzip pigpio.zip

>cd PIGPIO

>make

>sudo make install


Donwload FLASK for the embebeded web server

>sudo apt-get install python-flask python-dev

Get latest version

>mkdir SDKs

Get zmq lastest. If not CONFLATE does not work
>mkdir zmq
>chmod zmq
>wget http://download.zeromq.org/zeromq-3.2.5.tar.gz

Get cronoStamper software (this)
>git clone https://github.com/nachoplus/cronoStamper.git
