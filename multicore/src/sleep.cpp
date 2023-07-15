#include "sleep.h"

#include "audio.h"
#include "comms.h"
#include "led_control.h"
#include "networking.h"
#include "screen.h"

#include <Arduino.h>
#include <cstdint>

// RTC_DATA_ATTR means that this value is not stored in RAM, but
// rather in a small alternative memory used by the real-time clock.
// This memory is not powered down during deep sleep, so this value
// will be maintained across sleep-wake cycles.
RTC_DATA_ATTR uint16_t wakeFromSleepCounter = 0;

namespace sleep_mode {
    bool wokeFromSleep() {
        return wakeFromSleepCounter > 0;
    }

    namespace commands {
        void enterDeepSleep(uint32_t millisToSleep) {
            String sleepMsg = "Entering deep sleep mode.\n";
            sleepMsg += "I have slept " + String(wakeFromSleepCounter) + " times since last boot.\n";
            sleepMsg += "Wake scheduled for " + String(millisToSleep / 1000.0 / 60) + " minutes from now.";
            comms::sendDebugMessage(sleepMsg);
            // Send a single heartbeat. This is needed, because usually we're going back to sleep
            // right away during boot, before the main comms cycle has started.
            comms::forceHeartbeat();

            // Need to call this proactively, rather than wait for the next program loop,
            // because there will be no next program loop.
            networking::mqttSendReceive();

            wakeFromSleepCounter++;

            // We need to disable the parts of the flower microcontroller that are not
            // in the scope of esp32 low-power mode, which is the stuff on the secondary
            // board: the screen and the audio controller.
            screen::powerDown();
            audio::shutdownAudio();

            // Set all LEDs to black; if this is not done; they'll stay lit during
            // esp32 deep sleep mode.
            led_control::commands::clearPatterns();
            led_control::commands::setBrightness(0);
            // Brief pause (in the comms task) to allow the LED task to run (on the
            // other core), so that the LED shutdown specified above will take effect
            // before we enter sleep mode.
            delay(200);  // milliseconds

            uint32_t microsToSleep = millisToSleep * 1000;
            // The sole wake-up condition is the RTC (real-time clock) timer. By not
            // setting any other wake-up conditions, we cause all parts of the esp32
            // *except* the RTC (and the ULP co-processor) to power down.
            esp_sleep_enable_timer_wakeup(microsToSleep);
            // The system call to enter deep sleep mode. Nothing can execute after this;
            // control resumes at the start of setup() in main.cpp
            esp_deep_sleep_start();
        }
    } // namespace commands
} // namespace sleep_mode

