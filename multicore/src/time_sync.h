#ifndef TIME_SYNC_H
#define TIME_SYNC_H

#include <Arduino.h>

namespace time_sync
{
    // To be called at startup.
    void setupNTPClientAndSync();

    // To be called from the heartbeat method
    String getFormattedNTPTime();

    // Milliseconds that have passed since the event reference time
    // This is used as the trigger time for flower events like sound
    // and LED changes. This function runs fast enouch to call from
    // the LED control loop.  It's two function calls plus some math.
    //
    // If no event reference time has been set, or if NTP sync has never
    // run, the time since the event reference time is impossible to know,
    // and this function returns 0;
    //
    // We use this instead of a global time-since-epoch so that event times
    // can be specified using a single simple-data-type value. Giving times
    // since the unix epoch with millisecond precision requires at least two
    // values.
    unsigned long controlMillis();

    namespace commands {
        // Sets the "event reference time", relative to which eventMillis
        // values are defined.  referenceTimeSec is given in seconds
        // since the unix epoch.  This will be subtracted from the
        // true seconds since the epoch derived from NTP.
        void setEventReferenceTime(unsigned long referenceTimeSec);
    }
}

#endif // TIME_SYNC_H
