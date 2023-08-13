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

#include <cstdint>

namespace time_sync
{
    const uint16_t NTP_UPDATE_PERIOD_MILLIS = 60 * 1000;
    // Could be used for time zones.  We'll just use UTC.
    const uint16_t NTP_OFFSET = 0;
    const uint16_t NTP_TIMEOUT_MILLIS = 800;

    // State used for flower syncing
    uint32_t eventReferenceTimeSec = 0;

    // Whether we have ever synced successfully with NTP NTPClient.isTimeSet() doesn't work for this.
    bool haveSyncedWithNTP = false;

    WiFiUDP ntpUDP;
    NTPClient ntpClient(ntpUDP, config::CONTROLLER_IP_ADDRESS,
                        NTP_OFFSET, NTP_UPDATE_PERIOD_MILLIS);

    void setupNTPClientAndSync() {
        ntpClient.begin();
        ntpClient.setTimeout(NTP_TIMEOUT_MILLIS);

        // This is the first and probably most accurate NTP sync, since the current
        // thread has the whole CPU. Resyncing later is possible, and necessary
        // if the NTP server starts up after this flower does.
        commands::syncWithNTP();
    }

    String getFormattedNTPTime() {
        if (haveSyncedWithNTP) {
            return ntpClient.getFormattedTime() + "." + String((int)ntpClient.get_millis());
        } else {
            return "NTP has not synced.";
        }
    }

    // Number of milliseconds since the event reference time.
    uint32_t controlMillis()
    {
        // Unless we have both an NTP sync and an eventReferenceTime, the
        // controlMillis return value is meaningless.  As a fall-back, we
        // can use the system millis(). This lets many sync-independent
        // flower behaviors still be reasonable.
        if (!eventReferenceTimeSec || !haveSyncedWithNTP) {
            return millis();
        }

        // The assumption is that eventReferenceTimeSec is in the relatively recent
        // past (e.g. when the controller started up), so that the number of seconds
        // since then is small enough that when we multiply it by 1000, it won't
        // overflow an unsigned long (32 bits, max representable offset is about 50 days)
        uint32_t whole_seconds = ntpClient.getEpochTime() - eventReferenceTimeSec;
        uint32_t millis = (int) ntpClient.get_millis();
        return whole_seconds * 1000 + millis;
    }

    namespace commands {
        void setEventReferenceTime(uint32_t referenceTimeSec) {
            eventReferenceTimeSec = referenceTimeSec;
        }

        void syncWithNTP() {
            uint8_t num_attempts = 0;
            bool syncSuccessful = false;
            Serial.println("Getting NTP Time...");
            while (num_attempts++ < 3) {
                delay(2000);
                comms::sendDebugMessage("Attempting NTP sync...");
                syncSuccessful = ntpClient.forceUpdate();
                if (syncSuccessful) {
                    break;
                }
            }
            if (syncSuccessful) {
                haveSyncedWithNTP = true;
                comms::sendDebugMessage("Time from NTP: " + ntpClient.getFormattedTime());
                screen::commands::appendText("Got global time from NTP\n");
            }
            else {
                Serial.println("Failed to get time from NTP.");
                comms::sendDebugMessage("Failed to get time from NTP.");
            }
        }
    }
}