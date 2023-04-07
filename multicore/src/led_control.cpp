#include "led_control.h"
#include "comms.h"  // not a good idea?
#include "time_sync.h"
#include "music_sync.h"

#include <FastLED.h>

// IO pin to which the LED data line is soldered.
#define DATA_PIN 15

// puck is 41, flower+leaves is about 100
#define NUM_LEDS 100

namespace led_control {

    CRGB gLEDs[NUM_LEDS];
    uint8_t gHue = 100;  // default to a nice green at startup
    uint8_t gVal = 150;
    uint8_t gB; // drives gVal and setBrightness.
    uint8_t gDeltaB;

    void setupFastLED() {
        FastLED.addLeds<NEOPIXEL, DATA_PIN>(gLEDs, NUM_LEDS);

        // This turns on temporal dithering, which can only work
        // if FastLED.show() is called as often as possible.
        FastLED.setBrightness(100);

        // TEMP: register the beat handler as a callback. If this slows down
        // FPS too much, I should hard-code it in the music sync poller instead.
        music_sync::onBeat(&beatHappened);
    }

    // State variables for flashing.
    bool beatFlashingEnabled = true;
    unsigned long flashStartTime;
    unsigned long flashDurationMillis = 50;

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

        if (beatFlashingEnabled) {
            unsigned long controlTime = time_sync::controlMillis();
            bool inFlash = controlTime > flashStartTime && controlTime < flashStartTime + flashDurationMillis;
            if (inFlash) {
                // Override whatever color would have been drawn with white,
                // but stick to the current level of brightness
                fill_solid(gLEDs, NUM_LEDS, CHSV(0, 0, gB));
                //FastLED.setBrightness(128);
            }
        }

        // This is essential. Calling FastLED.show as often as possible
        // is what makes temporal dithering work.
        FastLED.show();
    }

    void beatHappened(unsigned long beatControlTime) {
        flashStartTime = beatControlTime;
    }

    namespace commands {
        void setHue(uint8_t new_hue) {
            gHue = new_hue;
            // Fill and push right away, don't wait for the next update
            // of the pulsing loop, to minimize latency.
            fill_solid(gLEDs, NUM_LEDS, CHSV(gHue, 255, gVal));
            FastLED.show();
        }

        void toggleBeatFlashing() {
            beatFlashingEnabled = !beatFlashingEnabled;
        }
    }
}