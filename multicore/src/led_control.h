#ifndef LED_CONTROL_H
#define LED_CONTROL_H

#include <FastLED.h>

namespace led_control
{
    // Should be run during setup()
    void setupFastLED();

    // Should be called as often as possible, from loop(), or from
    // a separate task's forever loop. Either way, that loop should
    // have no delay() or other time-consuming blocking calls.
    void mainLoop();

    // Respond to an led control command from the server. This is
    // called from the networking task.
    
    // These functions are generally called from the networking thread
    // after a server command is received. Dispatch is in comms.cpp
    namespace commands {
        // Set all LEDs to the given hue.
        void setHue(uint8_t new_hue);
    }
}

#endif // LED_CONTROL_H
