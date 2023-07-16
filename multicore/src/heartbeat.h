#ifndef HEARTBEAT_H
#define HEARTBEAT_H

#include "Arduino.h"  // For String

class Uptime {
 public:
   Uptime() : _start_time_millis(millis()){};
   // Returns the number of seconds since constructions
   uint32_t Seconds();
   // Formatted version of Seconds():  "15 sec", "22 min",  "20 hours", "2 days"
   String Formatted();

 private:
   uint32_t _start_time_millis;
};

class Heartbeat {
  public:
    void BeatIfItsTime();
    void Beat();
    const uint32_t HEARTBEAT_PERIOD_MILLIS = 5000;
  private:
    String _makeHeartbeatMessage();
    uint32_t _last_heartbeat_millis = 0;
    Uptime _uptime;
};

#endif // HEARTBEAT_H