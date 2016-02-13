__CronoStamper__
========

Introduction
------------

High precisión timestamping using raspberry GPIO.

It is based on pigpiod great daemon (http://abyz.co.uk/rpi/pigpio/index.html)

(https://raw.githubusercontent.com/nachoplus/cronoStamper/master/test/cronoStamper.png)

Nacho Mas - January 2016


__HARDWARE__
----------

Minidin8:

Black ->2
Red ->3
orange->gnd


__Installing from SD image__
----------

Just burn your SD card with the provided image using raspberry standard way.

boot the raspberry. It will get the IP from DHCP, if fail to bring up the eth0 interface delete the 
/etc/udev/rules.d/70-persistent-net.rules file on the SD card. (see http://raspberrypi.stackexchange.com/questions/26155/cloning-sd-card-causes-interface-eth0-does-not-exist for futher information)

log as root (defaul passwd: 'albaricoque', change it soon) and run the following commands:

>raspi-config

> ---> Expand Filesystem  -> //Do it


Then edit your /etc/network/interface to set the IP address and /home/cronos/cronostamper/config.py to customize the variables

cronostamper soft run under the user 'cronos' (passwd:albaricoque, change it soon)

Reboot again

__Installing from scrach__
----------

First get minibian from https://minibianpi.wordpress.com/download/
and make and SD as raspberry usual

boot the raspberry log as root (defaul passwd: 'raspberry', change it soon) and run the following commands:

###Basic packages
>apt-get update

>apt-get dist-upgrade

>raspi-config

> ---> Expand Filesystem  -> //Do it

>apt-get install nano apt-utils bash-completion rpi-update raspi-config 

>apt-get install minicom git unzip make gcc g++ python-pip

>rpi-update 

>reboot

###Setup high precisón GPS-PPS disciplined clock
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

>wget 

>tar zxvf ntp-4.2.8p6.tar.gz 

>cd ntp-4.2.8p6

>./configure --enable-linuxcaps

>make

>make install

>service ntp stop

>cp /usr/local/bin/ntp* /usr/bin/ && cp /usr/local/sbin/ntp* /usr/sbin/

Edit the configuration file:

>nano /etc/ntp.conf 

at the end of the file include this lines:

>\# GPS Serial data reference

>server 127.127.28.0

>fudge 127.127.28.0 

>\# GPS Serial data reference

>server 127.127.28.0 minpoll 4 maxpoll 4 prefer

>fudge 127.127.28.0 time1 0.140 refid GPS


Close and restart

>service ntp start

### Setup cronostamper specific

Get the pigpiod daemon http://abyz.co.uk/rpi/pigpio/index.html and compile

>wget abyz.co.uk/rpi/pigpio/pigpio.zip

>unzip pigpio.zip

>cd PIGPIO

>make

>sudo make install



Donwload FLASK for the embebeded web server

>sudo apt-get install python-flask python-dev

Get latest version

Get zmq lastest. CONFLATE does not work on stock version

>wget http://download.zeromq.org/zeromq-4.1.4.tar.gz

>tar xvzf zeromq-4.1.4.tar.gz

>cd zeromq-4.1.4

>./configure --without-libsodium

>./make

>./make install

Install the python bindings

>pip install pyzmq



Now add a new user to run cronostamper daemons under:

>adduser cronos

Log in that user and get cronoStamper software (this)

>git clone https://github.com/nachoplus/cronoStamper.git

### To run test and check
In order to run some test you need aditional stuff:

>apt-get install wiringpi gnuplot


### Start on boot

>nano /etc/rc.local 

at the end of the file include this lines:

>pigpiod

>/home/cronos/cronostamper/start.sh


