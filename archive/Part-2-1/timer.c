#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>

#include "time.h"

/** \brief timer facility */
static struct timeval timer_start;

void timer_reset(void)
{
	gettimeofday(&timer_start, NULL);
}

long timer_get(void)
{
	struct timeval now;
	gettimeofday(&now, NULL);
    long val = (now.tv_sec - timer_start.tv_sec) * 1000 +
		       (now.tv_usec - timer_start.tv_usec) / 1000;
    timer_reset();
    return val;
}