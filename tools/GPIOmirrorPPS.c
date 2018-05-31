/*
 * ppstest.c -- simple tool to monitor PPS timestamps
 *
 * Copyright (C) 2005-2007   Rodolfo Giometti <giometti@linux.it>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "timepps.h"

#include <pigpiod_if2.h>

#define PPS_PIN 18
#define PPS_MIRROR_PIN 4
#define PULSE_US  100

int pigpioCon;

void pulseHIGH()
{
	int trigger_status;
	trigger_status = gpio_write(pigpioCon, PPS_MIRROR_PIN,PI_HIGH);
	if (trigger_status < 0)
	   {
   		fprintf(stderr, "pigpio write HIGH failed.%u\n",trigger_status);
		exit(EXIT_FAILURE);
	   }
	fprintf(stdout, "PPS HIGH\n");
}


void pulseLOW()
{
	int trigger_status;
	trigger_status = gpio_write(pigpioCon, PPS_MIRROR_PIN,PI_LOW);
	if (trigger_status < 0)
	   {
   		fprintf(stderr, "pigpio write LOW failed.%u\n",trigger_status);
		exit(EXIT_FAILURE);
	   }
	fprintf(stdout, "PPS LOW\n");
}


void usage(char *name)
{
	fprintf(stderr, "usage: %s <ppsdev> [<ppsdev> ...]\n", name);
	exit(EXIT_FAILURE);
}

int main(int argc, char *argv[])
{

	/* Check the command line */
	if (argc < 2)
		usage(argv[0]);

	pigpioCon = pigpio_start(0, 0);
	if (pigpioCon < 0)
	   {
      		fprintf(stderr, "pigpio initialisation failed.\n");
		exit(EXIT_FAILURE);
	   }

	printf("Connected to pigpio daemon.\n");

	if (	set_mode(pigpioCon,PPS_MIRROR_PIN,PI_OUTPUT) < 0)
	   {
      		fprintf(stderr, "pigpio SET_MODE failed.\n");
		exit(EXIT_FAILURE);
	   }
	callback(pigpioCon,PPS_PIN,RISING_EDGE,pulseHIGH);
	callback(pigpioCon,PPS_PIN,FALLING_EDGE,pulseLOW);
	/* loop, printing the most recent timestamp every second or so */
	while (1) {
		usleep(100);
		//fprintf(stdout, ".\n");
	}

	pigpio_stop(pigpioCon);
	return 0;
}
