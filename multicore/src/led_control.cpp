#include "led_control.h"

#include "comms.h"  // not a good idea?
#include "config.h" // for LED_DATA_PIN
#include "led_patterns.h"
#include "sleep.h"
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
        FastLED.setBrightness(DEFAULT_BRIGHTNESS);

        // Set up the LEDs patterns to run before receiving any commands from
        // the control server.
        //
        // When waking from sleep, the common case is that we check in with the
        // command server and are told to go back to sleep right away. In this
        // case we want to leave the LEDs off. We don't want them to come on briefly
        // every time we wake and check.
        //
        // If we're not waking from sleep (i.e. we just booted because the flower
        // was plugged into power), then we want a nice-looking default.
        if (!sleep_mode::wokeFromSleep()) {
            // Default pattern is an independent idle, which will look OK in the absence
            // of any field coordination, and/or if the sync timer is not set.
            patterns.emplace_back(new led_patterns::IndependentIdle());
            patterns.emplace_back(new led_patterns::Raindrops(6, 3));
        } else {
            // When entering sleep mode for the first time, there's a weird behavior where
            // one or two LEDs in the strip light up white as the esp32 shuts down. This
            // clears such LEDs back to black when the flower wakes briefly before returning
            // to sleep.
            FastLED.clear(/* writedata= */true);
        }
    }

    void mainLoop() {
        // Start with all LEDs off; so any transient patterns can have noticeable effects
        fill_solid(gLEDs, NUM_LEDS, CRGB::Black);
        for (auto& pattern : patterns) {
            pattern->run(time_sync::controlMillis(), gLEDs);
        }

        // Unload any patterns that have finished
        EVERY_N_MILLISECONDS(500) {
            patterns.erase(std::remove_if(
                patterns.begin(), patterns.end(),
                [](const std::unique_ptr<led_patterns::Pattern>& p) {
                    bool done = p->isDone(time_sync::controlMillis());
                    if (done) {
                        comms::sendDebugMessage("Unloading finished pattern: " + p->name());
                    }
                    return done;
                }
            ), 
            patterns.end());
        }

        // This is essential. Calling FastLED.show as often as possible
        // is what makes temporal dithering work.
        FastLED.show();
    }

    namespace commands {

        void addPattern(const String &patternName, const String &parameters) {
            std::unique_ptr<led_patterns::Pattern> pattern = led_patterns::makePattern(patternName, parameters);
            if (pattern != nullptr) {
                comms::sendDebugMessage("Adding LED pattern: " + pattern->name());
                patterns.push_back(std::move(pattern));
            } else {
                comms::sendDebugMessage("Failed to initialize LED pattern.");
            }
        }

        void updatePattern(const String &patternName, const String &parameters) {
            std::unique_ptr<led_patterns::Pattern> newPattern = led_patterns::makePattern(patternName, parameters);
            bool alreadyHaveOne = false;
            for (std::unique_ptr<led_patterns::Pattern>& pattern : patterns) {
                if (pattern->name() == patternName) {
                    alreadyHaveOne = true;
                    pattern = std::move(newPattern);
                    comms::sendDebugMessage("Updated LED pattern: " + newPattern->descrip());
                }
            }
            if (!alreadyHaveOne) {
                patterns.push_back(std::move(newPattern));
                comms::sendDebugMessage("Added LED pattern: " + newPattern->descrip());
            }
        }

        void listPatterns() {
            String msg = "LED Patterns: ";
            for (auto& pattern : patterns) {
                msg += pattern->descrip() + ", ";
            } 
            if (msg.endsWith(", ")) {
                msg = msg.substring(0, msg.length() - 2);
            }
            comms::sendDebugMessage(msg);
        }

        void clearPatterns() {
            // TODO: why is the beatflash callback not getting unregistered at this point,
            // I expect all the patterns' destructors to be called.
            comms::sendDebugMessage("Clearing all LED patterns and resetting global brightness to "
                                    + String(DEFAULT_BRIGHTNESS));
            patterns.clear();
            FastLED.setBrightness(DEFAULT_BRIGHTNESS);
        }

        void setBrightness(uint8_t brightness) {
            FastLED.setBrightness(brightness);
        }
    }
}