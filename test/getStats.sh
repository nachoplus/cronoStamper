rm clock.dat
export PYTHONUNBUFFERED=yes
ssh  pi@nachoplus-rpi 'echo "nachoplus-rpi clock info";ntpq -p;echo "";ntpdc -c kerninfo' >clock.dat
echo "" >> clock.dat
ssh  pi@192.168.1.36 'echo "cronoStamper clock info";ntpq -p;echo "";ntpdc -c kerninfo' >>clock.dat
#ssh  -X pi@192.168.1.36  '/home/pi/ntp/loopGraph.plot' >cronoStamper.png
ssh  -X pi@nachoplus-rpi  '/home/pi/ntp/loopGraph.plot' >nachoplus.png
R --vanilla <test.R 
