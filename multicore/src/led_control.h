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

    // Called from the music sync time polling loop once for each beat.
    // Used for beat visualization mode.
    // beatControlTime is the value of the control time at which the beat
    // takes place. It's passed here to avoid extra calls to time_sinc::controlMillis()
    void beatHappened(unsigned long beatControlTime);
    
    // These functions are generally called from the networking thread
    // after a server command is received. Dispatch is in comms.cpp
    namespace commands {
        // Set all LEDs to the given hue.
        void setHue(uint8_t newHue);

        // When enabled, LEDs will flash white, at the current global brigthness,
        // for 50ms once for every beat according to the current BPM
        void toggleBeatFlashing();
    }
}

#endif // LED_CONTROL_H
