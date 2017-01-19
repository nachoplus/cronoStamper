#! /usr/bin/gnuplot
# Remember to check you have these lines in /etc/ntp.conf and that ntpd is actually running:
#    statsdir /var/log/ntpstats/
#    statistics loopstats peerstats clockstats
#    filegen loopstats file loopstats type day enable
#    filegen peerstats file peerstats type day enable
#    filegen clockstats file clockstats type day enable

# Resolution: fullscreen
#set term png size `xrandr | awk '/\*/{sub(/x/,",");print $1; exit}'`
set term png size 1500,1000 font ",8"
set grid
set bars 0.4
set y2tics
#set y2range [0:]
set ytics nomirror
set xdata time
set timefmt "%s"
set format x "%T"
local_time = `date +%s --utc -d "12:00:00 $(date +%z)"`
utc_time   = `date +%s --utc -d "12:00:00"`
localdifferencefromUTC = utc_time - local_time
timeoffsettoday = `date +%s --utc -d "today 0:00"` + localdifferencefromUTC
serialnumber="`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`"
hostname="`hostname`"
date="`date`"
set macro
line_number='int($0)'
set multiplot layout 2,2 rowsfirst title "Cronostamper Test. Date:".date."\nHostname:".hostname."Serial Number:".serialnumber

set title "PPS Reference Clock"
set ylabel "Clock offset (ms)"
set xlabel "Time"
plot \
"< grep -a '127.127.22.0' /var/log/ntpstats/peerstats|tail -200" u ($2+timeoffsettoday):($5*1000):($8*1000) w errorbars t 'PPS error'   lt 1,\
"< grep -a '127.127.22.0' /var/log/ntpstats/peerstats|tail -200" u ($2+timeoffsettoday):($5*1000) t 'PPS'   lt 3,\
0 w l lt -1

set title "GPS Reference Clock"
plot \
"< grep -a '127.127.28.0' /var/log/ntpstats/peerstats|tail -200" u ($2+timeoffsettoday):($5*1000):($8*1000) t 'GPS' w errorbars  lt 2,\
0 w l lt -1

set title "GPS vs PPS"
plot \
"< grep -a '127.127.22.0' /var/log/ntpstats/peerstats|tail -200" u ($2+timeoffsettoday):($5*1000) t 'PPS'    lt 1,\
"< grep -a '127.127.28.0' /var/log/ntpstats/peerstats|tail -200" u ($2+timeoffsettoday):($5*1000) t 'GPS'   lt 2,\
0 w l lt -1

set title "Clock ajustments"

set ylabel "Clock offset (ms)"
set y2label "Frequency offset (PPM or microsecons/second)"
plot \
  "<cat  /var/log/ntpstats/loopstats|tail -200" u ($2+timeoffsettoday):($3*1000):($5*1000/2) t "Clock offset" w errorlines lt 3 lw 1 pt 1, \
"<cat /var/log/ntpstats/loopstats|tail -200" u ($2+timeoffsettoday):($4):($6/2) axes x1y2 t "Frequency offset" w errorline lt 1 lw 1 pt 1, \
0 w l lt -1

pause mouse close
