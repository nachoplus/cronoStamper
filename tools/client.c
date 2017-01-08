/*
Cronostamper test suit:
This program is a simple client that show
the UTC time when PIN 11 is activated.

Nacho Mas January-2017
*/

#include <stdio.h>
#include <sys/time.h>
#include <wiringPi.h>
#include <time.h>

//#define MONOTONIC

// Which GPIO pin we're using
#define PIN 11
// How much time a change must be since the last in order to count as a change


// Current state of the pin
static volatile int state;

// Handler for interrupt
void handle(void) {
#ifdef MONOTONIC
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC,&now);
        printf("%u.%09u\n",now.tv_sec,now.tv_nsec);
#else
	struct timeval now;
	gettimeofday(&now, NULL);
        printf("%u.%06u\n",now.tv_sec,now.tv_usec);
#endif
}

int main(void) {
	// Init
	wiringPiSetupGpio();

        piHiPri (90) ;

	// Set pin to output in case it's not
	pinMode(PIN, OUTPUT);


	// Bind to interrupt
	wiringPiISR(PIN, INT_EDGE_RISING, &handle);


	// Waste time but not CPU
	for (;;) {
		sleep(1);
	}
}
