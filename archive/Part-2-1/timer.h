#ifndef TIMER
#define TIMER

/**
   \brief Set the timer to 0
   */
void timer_reset(void);

/**
   \brief Get the time and reset the time
   \return the value of the timer
   */
long timer_get(void);

#endif