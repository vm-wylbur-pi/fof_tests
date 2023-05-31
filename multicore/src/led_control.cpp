#include "led_control.h"

#include "comms.h"  // not a good idea?
#include "config.h" // for LED_DATA_PIN
#include "led_patterns.h"
#include "time_sync.h"
#include "music_sync.h"

#include <memory>
#include <FastLED.h>

namespace led_control {

    CRGB gLEDs[NUM_LEDS];
    uint8_t gHue = 100;  // default to a nice green at startup
    uint8_t gVal = 150;
    uint8_t gB; // drives gVal and setBrightness.
    uint8_t gDeltaB;

    void setupFastLED() {
        FastLED.addLeds<NEOPIXEL, LED_DATA_PIN>(gLEDs, NUM_LEDS);

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

    // Default pattern is an independent idle, which will look OK in the absence
    // of any field coordination, and/or if the sync timer is not set.
    std::unique_ptr<led_patterns::Pattern> currentPattern = std::unique_ptr<led_patterns::Pattern>(new led_patterns::IndependentIdle());

    void mainLoop() {
        currentPattern->run(time_sync::controlMillis(), gLEDs);

        // if (beatFlashingEnabled) {
        //     unsigned long controlTime = time_sync::controlMillis();
        //     bool inFlash = controlTime > flashStartTime && controlTime < flashStartTime + flashDurationMillis;
        //     if (inFlash) {
        //         // Override whatever color would have been drawn with medium-brightness white.
        //         fill_solid(gLEDs, NUM_LEDS, CHSV(0, 0, 128));
        //         FastLED.setBrightness(128);
        //     }
        // }

        // This is essential. Calling FastLED.show as often as possible
        // is what makes temporal dithering work.
        FastLED.show();
    }

    void beatHappened(unsigned long beatControlTime) {
        flashStartTime = beatControlTime;
    }

    namespace commands {
        void setHue(uint8_t newHue) {
            gHue = newHue;
            // Fill and push right away, don't wait for the next update
            // of the pulsing loop, to minimize latency.
            fill_solid(gLEDs, NUM_LEDS, CHSV(gHue, 255, gVal));
            FastLED.show();
        }

        void toggleBeatFlashing() {
            beatFlashingEnabled = !beatFlashingEnabled;
        }

        void runPattern(const String &patternName, const String &parameters) {
            std::unique_ptr<led_patterns::Pattern> pattern = led_patterns::makePattern(patternName, parameters);
            if (pattern != nullptr) {
                currentPattern = std::move(pattern);
                comms::sendDebugMessage("Switching to pattern: " + currentPattern->name());
            } else {
                comms::sendDebugMessage("Failed to initialize pattern. Staying with: " + currentPattern->name());
            }
        }
    }
}