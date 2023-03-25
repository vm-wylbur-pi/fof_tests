#ifndef LED_CONTROL_H
#define LED_CONTROL_H

#include <FastLED.h>

#define NUM_LEDS 41
#define DATA_PIN 15

namespace led_control
{
    // Should be run during setup()
    void setupFastLED();

    // Should be called as often as possible, from loop(), or from
    // a separate task's forever loop. Either way, that loop should
    // have no delay() or other time-consuming blocking calls.
    void mainLoop();
}

#endif // LED_CONTROL_H
