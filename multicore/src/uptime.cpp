#include "uptime.h"
#include "Arduino.h"

uint32_t Uptime::Seconds() {
    return (millis() - _start_time_millis) / 1000;
}

String Uptime::Formatted() {
    uint32_t seconds = Seconds();
    if (seconds < 60) {
        return String(seconds) + " sec";
    } else if (seconds < 60*60) {
        return String(seconds/60) + " min";
    } else if (seconds < 60*60*24) {
        return String(seconds / (60*60)) + " hours " +
               String(seconds % 60) + " min";
    } else {
        return String(seconds / (60*60*24)) + "days " +
               String(seconds % (60*60)) + " hours";
    }
}