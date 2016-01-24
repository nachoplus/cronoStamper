#! /usr/bin/gnuplot
# Remember to check you have these lines in /etc/ntp.conf and that ntpd is actually running:
#    statsdir /var/log/ntpstats/
#    statistics loopstats peerstats clockstats
#    filegen loopstats file loopstats type day enable
#    filegen peerstats file peerstats type day enable
#    filegen clockstats file clockstats type day enable

# Resolution: fullscreen
set term png size `xrandr | awk '/\*/{sub(/x/,",");print $1; exit}'`
set grid
set bars 0.4
set y2tics
#set y2range [0:]
set ytics nomirror
set xdata time
set timefmt "%s"
set format x "%T"
set title "NTP statistics"
set ylabel "Clock offset (ms)"
set y2label "Frequency offset (PPM)"
set xlabel "Time of day"
local_time = `date +%s --utc -d "12:00:00 $(date +%z)"`
utc_time   = `date +%s --utc -d "12:00:00"`
localdifferencefromUTC = utc_time - local_time
timeoffsettoday = `date +%s --utc -d "today 0:00"` + localdifferencefromUTC
plot \
  "<cat  /var/log/ntpstats/loopstats" u ($2+timeoffsettoday):($3*1000):($5*1000/2) t "Clock offset" w errorlines lt 1 lw 1 pt 187, \
"<cat  /var/log/ntpstats/loopstats" u ($2+timeoffsettoday):($4):($6/2) axes x1y2 t "Frequency offset" w errorline lt 7 pt 65, \
0 w l lt -1
pause mouse close
