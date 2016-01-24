rm clock.dat
export PYTHONUNBUFFERED=yes
ssh  pi@nachoplus-rpi 'echo "nachoplus-rpi clock info";ntpq -p;echo "";ntpdc -c kerninfo' >clock.dat
echo "" >> clock.dat
ssh  cronos@cronostamper 'echo "cronoStamper clock info";ntpq -p;echo "";ntpq -c kern' >>clock.dat
ssh  -X cronos@cronostamper  '/home/cronos/cronostamper/test/loopGraph.plot' >cronoStamper.png
ssh  -X pi@nachoplus-rpi  '/home/pi/ntp/loopGraph.plot' >nachoplus.png
R --vanilla <test.R 
