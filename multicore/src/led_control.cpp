#include "led_control.h"
#include "comms.h"  // not a good idea?
#include "time_sync.h"

#include <FastLED.h>

// IO pin to which the LED data line is soldered.
#define DATA_PIN 15

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

    // State variables for flashing implementation.  This is temprary; we'll
    // need better dispatch for multiple possible LED effects (maybe overlapping?)
    bool justFlashed = false;
    CRGB colorBeforeFlashing;
    unsigned long flashTimes[5];
    unsigned long flashDurationMillis = 50;

    void mainLoop() {
        // if (justFlashed)
        // {
        //     // I want the white flash to last for a single frame, with
        //     // no temporal dithering.
        //     fill_solid(gLEDs, NUM_LEDS, colorBeforeFlashing);
        //     FastLED.setBrightness(gB);
        // }

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

        unsigned long controlTime = time_sync::controlMillis();
        bool inFlash = false;
        int flashNum = 0;
        for (int i=0; i<5; i++) {
            if (controlTime > flashTimes[i] && controlTime < flashTimes[i] + flashDurationMillis) {
                inFlash = true;
                flashNum = i;              
            }
        }
        if (inFlash)
        {
            fill_solid(gLEDs, NUM_LEDS, CRGB(64, 64, 64));
            FastLED.setBrightness(128);
            gHue = 40*(flashNum+1);  // neat color shift between flashes.
            gB = 31;
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

        void flashWhiteFiveTimesSynced(unsigned long firstFlashTime) {
            // override command so I don't have to figure out what's in the 
            // immedate future during testing.
            firstFlashTime = (time_sync::controlMillis() / 1000 + 2) * 1000;
            for (int i=0; i<5; i++) {
                flashTimes[i] = firstFlashTime + (i * 1000);
            }
        }
    }
}