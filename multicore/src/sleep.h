#ifndef SLEEP_H
#define SLEEP_H

// Code for managing flower sleep mode.
// esp32 docs: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/sleep_modes.html
// tutorial used as a model: https://randomnerdtutorials.com/esp32-deep-sleep-arduino-ide-wake-up-sources/

#include <cstdint>

namespace sleep_mode {
    // Returns true if the esp32 has gone to sleep since the last time it
    // was powered up.  This can be used during the main-program setup()
    // function to know whether we are booting cold or starting from deep sleep.
    bool wokeFromSleep();

    namespace commands {
        // Put the esp32 into deep sleep mode. From a program logic point of view,
        // this is equivalent to turning the esp32 off (all RAM and other program state
        // is lost), followed by booting it up after the specified delay. Control will
        // resume by running setup() in main.cpp.
        //
        // Within the main.cpp setup(), use wokeFromSleep to distinguish
        // between waking from deep sleep and
        void enterDeepSleep(uint32_t millisToSleep);
    } // namespace commands
} // namespace sleep_mode

#endif // SLEEP_H