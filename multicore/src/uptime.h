#ifndef UPTIME_H
#define UPTIME_H

#include "Arduino.h"  // For String

class Uptime {
  public:
    Uptime() : _start_time_millis(millis()) {};
    // Returns the number of seconds since constructions
    uint32_t Seconds();
    // Formatted version of Seconds():  "15 sec", "22 min",  "20 hours", "2 days"
    String Formatted();
  private:
    uint32_t _start_time_millis;
};

#endif // UPTIME_H