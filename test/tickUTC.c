/* proof of concept. Try to correlate pigpio ticks with UTC time
following the sugestions https://github.com/joan2937/pigpio/issues/46
It does not work because t2-t1 is always greater than 46microseconds.
get_current_tick is the time consuming function.

 gcc tickUTC.c -lpigpiod_if2 -lrt  -pthread -o tickUTC

*/

#include <pigpio.h>
#include <stdio.h>
char *address ="localhost";
char *port ="8888";
double c;
uint32_t t1,t2;
int i=0;
int pi;
void main() {
pi=pigpio_start(address,port);
t1=0;
t2=10;

while ((t2-t1) > 2)
{
   t1 = get_current_tick(pi);
   c = time_time();
   t2 = get_current_tick(pi);
   i=i+1;
}
printf("%d %u  %u %u %f\n",i,t2-t1,t1,t2,c);
}

