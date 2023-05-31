#include "led_patterns.h"

#include <vector>

#include "comms.h"
#include "util.h"

#include <FastLED.h>

// LEDs in order from stem to tip
const uint8_t LEAF1_OUTWARD[] = { 0, 16,  1, 15,  2, 14,  3, 13,  4, 12,  5, 11,  6, 10,  7,  9,  8};
const uint8_t LEAF2_OUTWARD[] = {17, 33, 18, 32, 19, 31, 20, 30, 21, 29, 22, 28, 23, 27, 24, 26, 25};
const uint8_t LEAF3_OUTWARD[] = {34, 50, 35, 49, 36, 48, 37, 47, 38, 46, 39, 45, 40, 44, 41, 43, 42};

const uint8_t LEAF_STARTS[] = {LEAF1_START, LEAF2_START, LEAF3_START};

DEFINE_GRADIENT_PALETTE( LEAFY_GREENS_GP ) {
    0,   19,  96, 0, // semi-dark forest green
   77,  33, 156, 15, // mid emerald green
  179, 80, 137, 20, // yellowish green
  255,   19,  96, 0, // semi-dark forest green
};
const CRGBPalette16 leafyGreensPalette = LEAFY_GREENS_GP;

namespace led_patterns {

void SolidHue::run(uint32_t time, CRGB leds[NUM_LEDS]) {
    if (!_has_run && time > _start_time) {
        fill_solid(leds, NUM_LEDS, CHSV(_hue, 255, 100));
        _has_run = true;
        comms::sendDebugMessage("Ran SolidHue->run()");
    }
}

IndependentIdle::IndependentIdle() {
    _blossomHue = 0;
    // Start each point in each leaf at a random spot in the palette; each led
    // will rotate through the palette independently, to avoid spatial coherence.
    for (uint8_t i=0; i<LEAF_SIZE; i++) {
        _leafPaletteIdx[i] = random8();
    }
}

void IndependentIdle::run(uint32_t time, CRGB leds[NUM_LEDS]) {
    for (uint8_t leaf_start : LEAF_STARTS) {
        for (uint8_t i=0; i<LEAF_SIZE; i++) {
            leds[leaf_start + i] = ColorFromPalette(leafyGreensPalette, _leafPaletteIdx[i]);
        }
    }
    for (uint8_t i=BLOSSOM_START; i<BLOSSOM_END; i++) {
        // Simple hue for now. TODO: add some variation, probably with palette cycling
        leds[i] = CHSV(_blossomHue, 255, 100);
    }

    // Palette cycling for each point in each leaf.
    EVERY_N_MILLISECONDS(10) {
        for (uint8_t i = 0; i < LEAF_SIZE; i++) {
            _leafPaletteIdx[i]++;
        }
    }
}

std::unique_ptr<Pattern> makePattern(const String &patternName, const String &parameters) {
    std::vector<String> params = util::splitCommaSepString(parameters);

    // Parameters are
    //   hue: 0-255
    //   start_time: relative to control timer
    if (patternName == "SolidHue") {
        uint8_t hue = 0;
        uint32_t start_time = 0;
        if (params.size() >= 1) { hue = params[0].toInt(); }
        if (params.size() >= 2) { start_time = params[1].toInt(); }
        return std::unique_ptr<Pattern>(new SolidHue(hue, start_time));
    }
    if (patternName == "IndependentIdle") {
        return std::unique_ptr<Pattern>(new IndependentIdle());
    }

    comms::sendDebugMessage("Unknown LED pattern: " + patternName);
    return nullptr;
}

} // namespace led_patterns