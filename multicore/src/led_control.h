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
        // Add the given pattern to the stack of patterns, on top of all existing
        // patterns. Should not be run from the LED control task.
        void addPattern(const String& patternName, const String& parameters);

        // Echo the set of patterns, in order from bottom to top, as an MQTT debug message.
        void listPatterns();

        // Remove all currently active LED patterns, even if they're not done yet.
        void clearPatterns();
    }
}

#endif // LED_CONTROL_H
