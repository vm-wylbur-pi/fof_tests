#ifndef LED_PATTERNS_H
#define LED_PATTERNS_H

#include <memory>
#include <FastLED.h>

#include "led_control.h" // for NUM_LEDS
#include "music_sync.h"

// Constants defining the layout of LEDs across each flower,
// useful for defining patterns that move in defined ways relative
// to the flower structures.
#define LEAF1_START 0
#define LEAF2_START 17
#define LEAF3_START 34
#define LEAF_SIZE 17
#define BLOSSOM_START 51
#define BLOSSOM_END 111  // one past the end
#define BLOSSOM_SIZE 50

namespace led_patterns {

    // Abstract superclass for all patterns
    class Pattern {
      public:
        // Evaluate the pattern, altering the content of the leds array,
        // given an absolute control timer value.
        virtual void run(uint32_t time, CRGB leds[NUM_LEDS]) = 0;
        virtual String name() = 0;
    };

    // Solid hue at full saturation, sent to the LEDs exactly once, at the start time.
    class SolidHue : public Pattern {
      public:
        SolidHue(uint8_t hue, uint32_t start_time) : _hue(hue), _start_time(start_time) {};
        String name();
        void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
      private:
        uint8_t _hue;
        uint32_t _start_time;
    };

    // Idle pattern not related to a flower's position and not synced.
    // Gently varying greens in the leaves, and gently varying color in
    // the blossom centered around a random main hue.
    // As an "idle" pattern, this continues indefinitely.
    class IndependentIdle : public Pattern {
      public:
        IndependentIdle();
        void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
        String name() {return "IndependentIdle";};
      private:
        uint8_t _blossomHue;
        uint8_t _leafPaletteIdx[LEAF_SIZE];
    };

    // Change a single LED to white at medium brightness, cycling through all
    // LEDs in order; this gives an effect of a single dot bouncing around the
    // flower. Does not alter any LEDs besides the dot, so this is good for
    // testing pattern compositing.
    class RunningDot : public Pattern {
      public:
        void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
        String name() {return "RunningDot";};
      private:
        uint8_t _dotLocation = 0;
        uint8_t _dotDelta = 1;
    };

    class BeatFlash : public Pattern {
      public:
        void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
        String name() { return "BeatFlash"; };
      private:
        music_sync::MusicBeat _beatTracker;
        uint32_t _flashStartTime;
        uint32_t _flashDurationMillis = 50;  // could be made a parameter in the future.
    };

    // Pulse once, from black through to the given hue, then back to black.
    // Has a spatial progression, moving up through the leaves to the blossom,
    // then back down.
    // fades up and down from black, so this pattern should be applied on
    // top of an idling background.
    class HuePulse : public Pattern {
      public:
        HuePulse(uint8_t hue, uint32_t duration);
        void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
        String name() {return "HuePulse";};
    };

    // Interpret a string parameter as a moment in time. There are two formats:
    //  +1234:  Run the pattern starting 1234 milliseconds in the future.
    //  1234:   Run the pattern at absolute control time 1234.
    uint32_t parseStartTime(const String& startTimeParameter);

    // Construct a pattern object of the specified name and parameters.
    std::unique_ptr<Pattern> makePattern(const String& patternName, const String& parameters);
}  // namespace led_patterns

#endif // LED_PATTERNS_H