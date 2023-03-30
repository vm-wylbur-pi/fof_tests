#include "led_control.h"

#include <FastLED.h>

// First developmen board
// #define DATA_PIN 15
// Development board with the audio interface
#define DATA_PIN 13

// puck is 41, flower+leaves is about 100
#define NUM_LEDS 100

namespace led_control {

    CRGB gLEDs[NUM_LEDS];
    uint8_t gHue = 0;
    uint8_t gVal = 150;
    uint8_t gB; // drives gVal and setBrightness.
    uint8_t gDeltaB;

    void setupFastLED() {
        FastLED.addLeds<NEOPIXEL, DATA_PIN>(gLEDs, NUM_LEDS);

        // This turns on temporal dithering, which can only work
        // if FastLED.show() is called as often as possible.
        FastLED.setBrightness(100);
    }

    
    void mainLoop() {
        /// Vary gVal & dithering brightness within a low-medium range.
        // The purpose is to have the flower in a continuous smooth
        // brightness oscillation that depends on temporal dithering. Any
        // interruption in LED contol throughput should be visible as
        // pulse freezing or stuttering.
        EVERY_N_MILLISECONDS(10) {
            if (gB < 32) {
                gB = 31;
                gDeltaB = 1;
            } else if (gB > 128) {
                gB = 129;
                gDeltaB = -1;
            }
            gB += gDeltaB;
            gVal = gB;
            FastLED.setBrightness(gB);
            fill_solid(gLEDs, NUM_LEDS, CHSV(gHue, 255, gVal));
        }

        // This is essential. Calling FastLED.show as often as possible
        // is what makes temporal dithering work.
        FastLED.show();
    }

    namespace commands {
        void setHue(uint8_t new_hue) {
            gHue = new_hue;
            // Fill and push right away, don't wait for the next update
            // of the pulsing loop, to minimize latency.
            fill_solid(gLEDs, NUM_LEDS, CHSV(gHue, 255, gVal));
            FastLED.show();
        }
    }
}