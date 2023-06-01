#ifndef LED_CONTROL_H
#define LED_CONTROL_H

#include <FastLED.h>

#define NUM_LEDS 111

namespace led_control
{
    // Should be run during setup()
    void setupFastLED();

    // Should be called as often as possible, from loop(), or from
    // a separate task's forever loop. Either way, that loop should
    // have no delay() or other time-consuming blocking calls.
    void mainLoop();
    
    // These functions are generally called from the networking thread
    // after a server command is received. Dispatch is in comms.cpp
    namespace commands {
        // Set all LEDs to the given hue.
        void setHue(uint8_t newHue);

        // Schedule the given pattern to run according to its parameters.
        void runPattern(const String& patternName, const String& parameters);

        // Echo the set of patterns as an MQTT debug message.
        void listPatterns();

        // Remove all currently active LED patterns, even if they're not done yet.
        void clearPatterns();
    }
}

#endif // LED_CONTROL_H
