#include "time_sync.h"
#include "comms.h"
#include "config.h"  // For NTP server IP address
#include "networking.h"
#include "screen.h"

#include <Arduino.h>
// This is the modified version of the standard Library,
// with millisecond support added.
// See ../lib/NTPClient/README.txt for details and links.
#include <NTPClient.h>
#include <WiFiUdp.h>

namespace time_sync
{
    const uint16_t NTP_UPDATE_PERIOD_MILLIS = 60 * 1000;
    // Could be used for time zones.  We'll just use UTC.
    const uint16_t NTP_OFFSET = 0;
    const uint16_t NTP_TIMEOUT_MILLIS = 800;

    unsigned long eventReferenceTimeSec = 0;

    WiFiUDP ntpUDP;
    NTPClient ntpClient(ntpUDP, config::CONTROLLER_IP_ADDRESS,
                        NTP_OFFSET, NTP_UPDATE_PERIOD_MILLIS);

    void syncWithNTP() {
        uint8_t num_attempts = 0;
        Serial.println("Getting NTP Time...");
        comms::sendDebugMessage("Getting NTP Time...");
        while (ntpClient.update() != 1)
        {
            delay(2000);
            ntpClient.forceUpdate();
            if (++num_attempts > 3) {
                break;
            }
        }
        if (ntpClient.isTimeSet()) {
            comms::sendDebugMessage("Time from NTP: " + ntpClient.getFormattedTime());
            screen::commands::appendText("Got global time from NTP\n");
        } else {
            Serial.println("Failed to get time from NTP.");
            comms::sendDebugMessage("Failed to get time from NTP.");
        }
    }

    void setupNTPClientAndSync() {
        ntpClient.begin();
        ntpClient.setTimeout(NTP_TIMEOUT_MILLIS);

        // This is the only time we run NTP syncing, since we know
        // we'll have the whole CPU, and we don't expect clock drift
        // to matter.  We could run this more often if we notice clock
        // drift.
        syncWithNTP();
    }

    String getFormattedNTPTime() {
        if (ntpClient.isTimeSet()) {
            return ntpClient.getFormattedTime() + "." + String((int)ntpClient.get_millis());
        } else {
            return "NTP has not synced.";
        }
    }

    // Number of milliseconds since the event reference time.
    unsigned long controlMillis()
    {
        // This is initialized to zero above, so if it's still zero, that means
        // We've never set a reference time, and 
        if (!eventReferenceTimeSec) {
            return 0;
        }

        // If NTP sync has never run, then we can't work out the time since
        // the 
        if (!ntpClient.isTimeSet()) {
            return 0;
        }

        // The assumption is that eventReferenceTimeSec is in the relatively recent
        // past (e.g. when the controller started up), so that the number of seconds
        // since then is small enough that when we multiply it by 1000, it won't
        // overflow an unsigned long (32 bits, max representable offset is about 50 days)
        unsigned long whole_seconds = ntpClient.getEpochTime() - eventReferenceTimeSec;
        unsigned long millis = (int) ntpClient.get_millis();
        return whole_seconds * 1000 + millis;
    }

    namespace commands {
        void setEventReferenceTime(unsigned long referenceTimeSec) {
            eventReferenceTimeSec = referenceTimeSec;
        }
    }
}