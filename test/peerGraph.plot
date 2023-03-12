#! /usr/bin/gnuplot
# Remember to check you have these lines in /etc/ntp.conf and that ntpd is actually running:
#    statsdir /var/log/ntpstats/
#    statistics loopstats peerstats clockstats
#    filegen loopstats file loopstats type day enable
#    filegen peerstats file peerstats type day enable
#    filegen clockstats file clockstats type day enable

# Resolution: fullscreen
#set term png size `xrandr | awk '/\*/{sub(/x/,",");print $1; exit}'`

#GET parms througth enviroment and defaults
samples="`echo $_CLK_SAMPLES`"
peer0="`echo $_NTP_INTERNET_PEER0`"
peer1="`echo $_NTP_INTERNET_PEER1`"
print samples,peer0,peer1

set term png size 1500,1000 font ",8"
#set term svg size 1500,1000 font ",8"
set grid
set bars 0.4
set y2tics
#set y2range [0:]
set ytics nomirror
set xdata time
#set timefmt "%s"
set timefmt "%Y-%m-%d %H:%M:%S"
#set format x "%T"
set format x "%m-%d\n%H:%M"
local_time = `date +%s --utc -d "12:00:00 $(date +%z)"`
utc_time   = `date +%s --utc -d "12:00:00"`
localdifferencefromUTC = utc_time - local_time
timeoffsettoday = `date +%s --utc -d "today 0:00"` + localdifferencefromUTC
serialnumber="`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`"
hostname="`hostname`"
date="`date`"
set macro
line_number='int($0)'


set multiplot layout 2,2 rowsfirst title "Cronostamper Test. Date:".date." Samples:".samples."\nHostname:".hostname."Serial Number:".serialnumber

set title "RMS offset from UTC"
set ylabel "Clock offset (s)"
set xlabel "Time"
set label 1 "System Clock RMS deviation from\nfrom the Reference Clock (usually the PPS signal)" at graph 0.05,0.95
plot \
"<cat /var/log/chrony/tracking.log|tail -$_CLK_SAMPLES|sed '/^=/d'|sed '/^ /d'" u 1:14 t 'RMS Offset' with lines   lt 3,\
0 w l lt -1

set title "GPS  Clock"
unset label 1
set label 2 "GPS Time deviation from System Clock.\nMostly due to GPS serial interface latency" at graph 0.05,0.95
plot \
"< grep -a 'GPS' /var/log/chrony/statistics.log|tail -$_CLK_SAMPLES" u 1:5:6 w errorbars t 'GPS error'   lt 1,\
"< grep -a 'GPS' /var/log/chrony/statistics.log|tail -$_CLK_SAMPLES" u 1:5 t 'GPS'   lt 3,\
0 w l lt -1

set title "Internet Server"
unset label 2
set label 3 "System Clock deviation as from\nsome internet stratum 2 servers.\nNot used. Show as reference." at graph 0.05,0.95
plot \
"< grep -a $_NTP_INTERNET_PEER0 /var/log/chrony/measurements.log|tail -$_CLK_SAMPLES" u 1:12 t peer0   lt 1,\
"< grep -a $_NTP_INTERNET_PEER1 /var/log/chrony/measurements.log|tail -$_CLK_SAMPLES" u 1:12 t peer1   lt 2,\
0 w l lt -1

set title "Clock ajustments"
unset label 3
set label 4 "Raspberry cristal oscilator drift and Systen Clock deviation\nfrom the Reference Clock (usually the PPS signal)" at graph 0.05,0.95
set ylabel "Clock offset (s)"
set y2label "Frequency offset (PPM or microsecons/second)"
plot \
"<cat  /var/log/chrony/tracking.log|tail -$_CLK_SAMPLES" u 1:7:10 w errorbars t "Clock offset"   lt 1,\
"<cat  /var/log/chrony/tracking.log|tail -$_CLK_SAMPLES" u 1:7:10 w l t ""   lt 1,\
"<cat  /var/log/chrony/tracking.log|tail -$_CLK_SAMPLES" u 1:5:6 w errorbars axes x1y2 t "Frequency correction"   lt 3,\
"<cat  /var/log/chrony/tracking.log|tail -$_CLK_SAMPLES" u 1:5:6 w l axes x1y2 t ""   lt 3,\
0 w l lt -1


#pause mouse close
