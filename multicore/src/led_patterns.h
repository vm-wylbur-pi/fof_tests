#ifndef LED_PATTERNS_H
#define LED_PATTERNS_H

#include <FastLED.h>

#include "led_control.h" // for NUM_LEDS

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
        // given an offset in milliseconds from the start of the pattern.
        virtual void run(uint32_t time, CRGB leds[NUM_LEDS]) = 0;
        virtual String name() = 0;
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
}  // namespace led_patterns

#endif // LED_PATTERNS_H