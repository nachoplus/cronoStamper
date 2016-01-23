#include <stdio.h>
#include <sys/time.h>
#include <wiringPi.h>
#include <time.h>

struct timespec diff(struct timespec start, struct timespec end);

//#define MONOTONIC

#define OUTPUT_PIN 7
int main (void)
{
  wiringPiSetupGpio();
  piHiPri (90) ;
  pinMode (OUTPUT_PIN, OUTPUT) ;
#ifdef MONOTONIC
    struct timespec tstart,tend;
    clock_gettime(CLOCK_MONOTONIC,&tstart);
#else
    struct timeval tstart;
    gettimeofday(&tstart, NULL);
#endif
    digitalWrite (OUTPUT_PIN, HIGH) ;
#ifdef MONOTONIC
    clock_gettime(CLOCK_MONOTONIC,&tend);
#endif
    usleep (10000) ;
    digitalWrite (OUTPUT_PIN,  LOW) ;
    //usleep (10000) ;
    usleep (990000) ;

#ifdef MONOTONIC
    struct timespec latency=diff(tstart,tend);
    printf("%u.%09u\n",tstart.tv_sec,tstart.tv_nsec);
    //printf(" %u.%09u\n",tend.tv_sec,tend.tv_nsec);
    //printf("%u.%09u\n",latency.tv_sec,latency.tv_nsec);
#else
    printf("%u.%06u\n",tstart.tv_sec,tstart.tv_usec);
#endif


  return 0 ;
}

struct timespec diff(struct timespec start,struct timespec end)
{
	struct timespec temp;
        //printf("ns: %09u %09u\n",end.tv_nsec,start.tv_nsec);
	if ((end.tv_nsec-start.tv_nsec)<0) {
		printf("!");
		temp.tv_sec = end.tv_sec-start.tv_sec-1;
		temp.tv_nsec = 1000000000+end.tv_nsec-start.tv_nsec;
	} else {
		temp.tv_sec = end.tv_sec-start.tv_sec;
		temp.tv_nsec = end.tv_nsec-start.tv_nsec;
	}
	return temp;
}
