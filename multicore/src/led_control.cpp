#include "led_control.h"

#include "comms.h"  // not a good idea?
#include "config.h" // for LED_DATA_PIN
#include "led_patterns.h"
#include "time_sync.h"
#include "music_sync.h"

#include <memory>
#include <vector>
#include <FastLED.h>

namespace led_control {

    CRGB gLEDs[NUM_LEDS];

    // The set of currently-active LED patterns.
    std::vector<std::unique_ptr<led_patterns::Pattern>> patterns = {};

    void setupFastLED() {
        FastLED.addLeds<NEOPIXEL, LED_DATA_PIN>(gLEDs, NUM_LEDS);

        // This turns on temporal dithering, which can only work
        // if FastLED.show() is called as often as possible.
        FastLED.setBrightness(100);

        // Default pattern is an independent idle, which will look OK in the absence
        // of any field coordination, and/or if the sync timer is not set.
        patterns.emplace_back(new led_patterns::IndependentIdle());
        patterns.emplace_back(new led_patterns::Raindrops(12, 3));
    }

    void mainLoop() {
        // Start with all LEDs off; so any transient patterns can have noticeable effects
        fill_solid(gLEDs, NUM_LEDS, CRGB::Black);
        for (auto& pattern : patterns) {
            pattern->run(time_sync::controlMillis(), gLEDs);
        }

        // This is essential. Calling FastLED.show as often as possible
        // is what makes temporal dithering work.
        FastLED.show();
    }

    namespace commands {

        void runPattern(const String &patternName, const String &parameters) {
            std::unique_ptr<led_patterns::Pattern> pattern = led_patterns::makePattern(patternName, parameters);
            if (pattern != nullptr) {
                comms::sendDebugMessage("Adding LED pattern: " + pattern->name());
                patterns.push_back(std::move(pattern));
            } else {
                comms::sendDebugMessage("Failed to initialize LED pattern.");
            }
        }

        void listPatterns() {
            String msg = "LED Patterns: ";
            for (auto& pattern : patterns) {
                msg += pattern->name() + ", ";
            } 
            if (msg.endsWith(", ")) {
                msg = msg.substring(0, msg.length() - 2);
            }
            comms::sendDebugMessage(msg);
        }

        void clearPatterns() {
            // TODO: why is the beatflash callback not getting unregistered at this point,
            // I expect all the patterns' destructors to be called.
            comms::sendDebugMessage("Clearing all LED patterns.");
            patterns.clear();
        }
    }
}