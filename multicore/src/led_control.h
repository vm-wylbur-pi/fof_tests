#ifndef LED_CONTROL_H
#define LED_CONTROL_H

#include <FastLED.h>

#define NUM_LEDS 111

namespace led_control
{
    // global FastLED brightness, used when clearing all patterns and when
    // receiving a setBrigtness command with no brightness parameter specified.
    const uint8_t DEFAULT_BRIGHTNESS = 100;

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

        // Modify a pattern in-place.  When we receive this command
        //   - If we already have one in the stack, update it with the given parameters
        //   - Otherwise, instantiate a new one with the given parameters.
        void updatePattern(const String &patternName, const String &parameters);

        // All patterns with given name are removed from the current LED
        // pattern stack.
        void removePattern(const String &patternName);

        // Echo the set of patterns, in order from bottom to top, as an MQTT debug message.
        void listPatterns();

        // Remove all currently active LED patterns, even if they're not done yet.
        // Resets the global brightness to its boot-time default.
        void clearPatterns();

        // Set the global FastLED brightness, which is implemented via time dithering.
        // Most LED patterns do not adjust this value, so it's useful as an overall
        // control to madulate or boost other patterns. Values below 10 can cause 
        // color artifacts and break smooth patterns.
        void setBrightness(uint8_t brightness);
    }
}

#endif // LED_CONTROL_H
