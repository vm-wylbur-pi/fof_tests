#include "led_patterns.h"

#include <vector>
#include <cmath>
#include <cstdint>

#include "comms.h"
#include "music_sync.h"
#include "time_sync.h"
#include "util.h"

#include <FastLED.h>

// LEDs in order from stem to tip
const uint8_t LEAF1_OUTWARD[] = { 0, 16,  1, 15,  2, 14,  3, 13,  4, 12,  5, 11,  6, 10,  7,  9,  8};
const uint8_t LEAF2_OUTWARD[] = {17, 33, 18, 32, 19, 31, 20, 30, 21, 29, 22, 28, 23, 27, 24, 26, 25};
const uint8_t LEAF3_OUTWARD[] = {34, 50, 35, 49, 36, 48, 37, 47, 38, 46, 39, 45, 40, 44, 41, 43, 42};


// Mappping from the index of an LED to how far it is from the ground, conceptually.
// The goal is that lighting up the LEDs from lowest to highest value according to
// this mapping will look like light rising up the stem and outward along the leaves
// and blossom.
const uint8_t LED_HEIGHTS[] = {
    // 1st half of leaf 1, stem to tip:
    20, 21, 22, 23, 24, 25, 26, 27, 28,
    // 2nd half of Lea 2, tip back to stem:
    27, 26, 25, 24, 23, 22, 21, 20,

    // 1st half of leaf 2, stem to tip:
    30, 31, 32, 33, 34, 35, 36, 37, 38,
    // 3nd half of Leaf 3, tip back to stem:
    37, 36, 35, 34, 33, 32, 31, 30,

    // 1st half of leaf 2, stem to tip:
    40, 41, 42, 43, 44, 45, 46, 47, 48,
    // 4nd half of Leaf 4, tip back to stem:
    47, 46, 45, 44, 43, 42, 41, 40,

    // Inner loop of blossom (25 LEDs)
    50, 50, 50, 50, 50, 50, 50, 50, 50, 50,
    50, 50, 50, 50, 50, 50, 50, 50, 50, 50,
    50, 50, 50, 50, 50,
    // Oouter loop of blossom (35 LEDs)
    60, 60, 60, 60, 60, 60, 60, 60, 60, 60,
    60, 60, 60, 60, 60, 60, 60, 60, 60, 60,
    60, 60, 60, 60, 60, 60, 60, 60, 60, 60,
    60, 60, 60, 60, 60
};

const uint8_t LEAF_STARTS[] = {LEAF1_START, LEAF2_START, LEAF3_START};

DEFINE_GRADIENT_PALETTE( LEAFY_GREENS_GP ) {
    0,   19,  96, 0, // semi-dark forest green
   77,  33, 156, 15, // mid emerald green
  179, 80, 137, 20, // yellowish green
  255,   19,  96, 0, // semi-dark forest green
};
const CRGBPalette16 leafyGreensPalette = LEAFY_GREENS_GP;

namespace led_patterns {

String SolidHue::name() {
    return "SolidHue(" + String(_hue) + ", " + String(_start_time) + ")";
}

void SolidHue::run(uint32_t time, CRGB leds[NUM_LEDS]) {
    if (time > _start_time) {
        fill_solid(leds, NUM_LEDS, CHSV(_hue, 255, 100));
    }
}

String HuePulse::name() {
    return "HuePulse(hue=" + String(_hue) + ", brightness=" + String(_brightness) + 
           ", startTime=" + String(_startTime) + ", rampDuration=" + String(_rampDuration) +
           ", peakDuration=" + String(_peakDuration) + ")";
}

bool HuePulse::isDone(uint32_t time) {
    return time > (_startTime + 2*_rampDuration + _peakDuration + 600);
}

void HuePulse::run(uint32_t time, CRGB leds[NUM_LEDS]) {
    // Nothing to do yet.
    if (time < _startTime) return;
    // Full pattern has finished; don't do any unnecessary work.
    // TODO: replace 60, which is hard-coded as the max delayDueToHeight
    if (time > _startTime + 2*_rampDuration + _peakDuration + 600) return;

    for (int i=0; i<NUM_LEDS; i++) {
        uint8_t height = LED_HEIGHTS[i];
        // TODO: This could be more sophisticated. For now, accept the arbitrary height
        //       scale as literal milliseconds.
        uint32_t delayDueToHegiht = height * 10;
        // How far into pattern execution (in ms) is the LED at index i
        uint32_t patternTime = time - _startTime - delayDueToHegiht;

        // The pattern follows a trapezoid shape: linear ramp up to flat peak, linear ramp down
        // The leaves ramp down right after ramping up; only the blossom holds at the peak.
        // The vertical axis here is alpha, the compositing parameter. The pattern is drawn in
        // constant brightness but blended a varying amount with the background pattern(s).
        //   |     _________________________
        //   |    /\                        \      
        // α |   /  \                        \
        //   |  /    \  <-- leaves ramp       \  <-- blossom ramps down
        //   | /      \     down immediately   \     after holding at peak
        //   |-----------------------------------------------------------------
        //    increasing patternTime ->

        // Default alpha is zero, which means leave the background pattern unchanged.
        _alpha[i] = 0;

        // Case 0: pulse hasn't reached this part of the flower yet.
        if (patternTime < 0) continue;
        // Case 1: ramping up. Same for leaves and blossom.
        if (patternTime < _rampDuration) {
            _alpha[i] = 255 * patternTime / _rampDuration;
            continue;
        }
        // Split behavior between the leaves and blossom
        if (i < BLOSSOM_START) {
            // leaves:  immediately ramp down
            if (patternTime < 2 * _rampDuration) {
                // Ramp the leaves back down to black
                uint32_t timeIntoRamp = patternTime - _rampDuration;
                _alpha[i] = 255 - 255 * timeIntoRamp / _rampDuration;
                continue;
            }
        } else {
            // Blossom: hold at peak brightness for the given duration
            if (patternTime < _rampDuration + _peakDuration) {
                // Hold at peak brightness
                _alpha[i] = _brightness;
                continue;
            }
            if (patternTime < _rampDuration + _peakDuration + _rampDuration) {
                // Ramp the blossom back down to black
                uint32_t timeIntoRamp = patternTime - _rampDuration - _peakDuration;
                _alpha[i] = 255 - 255 * timeIntoRamp / _rampDuration;
                continue;
            }
        }
    }

    // Alpha-compositing with patterns under this one.
    // I tried this in HSV space; it looked worse.
    for (int i=0; i<NUM_LEDS; i++) {
        CRGB target = CHSV(_hue, 255, _brightness);
        leds[i].r = lerp8by8(leds[i].r, target.r, _alpha[i]);
        leds[i].g = lerp8by8(leds[i].g, target.g, _alpha[i]);
        leds[i].b = lerp8by8(leds[i].b, target.b, _alpha[i]);
    }
}

String FairyVisit::name() {
    return "FairyVisit(visitDuration=" + String(_visitDuration) + ")";
}

bool FairyVisit::isDone(uint32_t time) {
    return time > _startTime + _visitDuration;
}

void FairyVisit::run(uint32_t time, CRGB leds[NUM_LEDS]) {
    if (_lastUpdateTime == 0) {
        // First time running. Initialize state.
        _startTime = time;
        _lastUpdateTime = time;  // so the first fairy location update is a no-op.
        _fairyLocation = random8(NUM_LEDS);
    }
    if (time > _startTime + _visitDuration) {
        // Fairy is gone from this flower, so draw nothing.
        // We're just waiting for this pattern to get unloaded via isDone
        return;
    }

    // Rendering
    //   Fairy is a bright white area with dim edges that fade away spatially from
    //   its logical (floating point) location.
    const int8_t fairyDiameter = 2;
    const CRGB FAIRY_COLOR(255,255,255);  // We could make this a parameter if needed.
    for (int offset=-fairyDiameter; offset<fairyDiameter; offset++) {
        uint8_t led_index = std::round(_fairyLocation) + offset;
        if (led_index >= 0 & led_index < NUM_LEDS) {
            // Fall-off linearly from fairy center
            float distanceFromFairy = abs(led_index - _fairyLocation);
            fract8 alpha = std::round(255 * distanceFromFairy / fairyDiameter);
            leds[led_index].r = lerp8by8(leds[led_index].r, FAIRY_COLOR.r, alpha);
            leds[led_index].g = lerp8by8(leds[led_index].g, FAIRY_COLOR.g, alpha);
            leds[led_index].b = lerp8by8(leds[led_index].b, FAIRY_COLOR.b, alpha);
        }
    }

    // Update fairy location. This runs in every loop so that the fairy
    // can have smooth motion at any speed.
    float secsSinceLastUpdate = (time - _lastUpdateTime) / 1000.0;
    _fairyLocation += _fairySpeed * secsSinceLastUpdate;

    // Bounce the fairy of each end of the LED strip if it went out of bounds.
    if (_fairyLocation < 0 || _fairyLocation > NUM_LEDS - 1) {
        _fairySpeed = -_fairySpeed;
    }

    EVERY_N_MILLISECONDS(100) {
        // Reverse direction at random a few times per second.
        // Faries are unpredictable and playful.
        if (random8() % 3 == 0) {
            _fairySpeed = -_fairySpeed;
        }
    }

    _lastUpdateTime = time;
}

IndependentIdle::IndependentIdle() {
    _blossomHue = 0;
    // Start each point in each leaf at a random spot in the palette; each led
    // will rotate through the palette independently, to avoid spatial coherence.
    for (uint8_t i=0; i<LEAF_SIZE; i++) {
        _leafPaletteIdx[i] = random8();
    }
}

String Raindrops::name() {
    return "Raindrops(" + String(_raindropsPerSecond) + ", " + String(_fadeSpeed) + ")";
}

Raindrops::Raindrops() {
    // Initialize owned array so non-raindrop spots won't write random data to the shared array.
    fill_solid(_leds, NUM_LEDS, CRGB::Black);
}

void Raindrops::run(uint32_t time, CRGB leds[NUM_LEDS]) {
    if (time > _nextRaindropTime) {
        uint8_t raindropIdx = random8(NUM_LEDS);
        _leds[raindropIdx] = CRGB(150,150,150);
        _nextRaindropTime = time + 1000 / _raindropsPerSecond;
    }
    // Fades the raindrops only, not the shared leds array containing whatever
    // the raindrops are on top of.
    fadeToBlackBy(_leds, NUM_LEDS, _fadeSpeed);

    for (uint8_t i=0; i<NUM_LEDS; i++) {
        leds[i] += _leds[i];
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

void RunningDot::run(uint32_t time, CRGB leds[NUM_LEDS]) {
    leds[_dotLocation] = CRGB(100, 100, 100);
    EVERY_N_MILLISECONDS(10) {
        if (_dotLocation == 0) {
            _dotDelta = 1;  // Bounce off bottom 
        }
        if (_dotLocation >= NUM_LEDS+1) {
            _dotDelta = -1; // Bounce off top.
        }
      _dotLocation += _dotDelta;
    }
}

void BeatFlash::run(uint32_t time, CRGB leds[NUM_LEDS]) {
    uint32_t beatTime = _beatTracker.checkForBeat();
    if (beatTime) {
      _flashStartTime = beatTime;
      comms::sendDebugMessage("Beat flash at control time " + String(beatTime));
    }
    bool inFlash = time > _flashStartTime && time < _flashStartTime + _flashDurationMillis;
    if (inFlash) {
        fill_solid(leds, NUM_LEDS, CHSV(0, 0, 128));
    }
}

uint32_t parseStartTime(const String &startTimeParameter) {
    if (startTimeParameter.startsWith("+")) {
        const uint32_t offset = startTimeParameter.substring(1).toInt();
        return time_sync::controlMillis() + offset;
    } else {
        return startTimeParameter.toInt();
    }
}

std::unique_ptr<Pattern> makePattern(const String& patternName, const String& parameters) {
    std::vector<String> params = util::splitCommaSepString(parameters);

    // Parameters are
    //   hue: 0-255
    //   start_time: relative to control timer
    if (patternName == "SolidHue") {
        uint8_t hue = 0;
        uint32_t start_time = 0;
        if (params.size() >= 1) { hue = params[0].toInt(); }
        if (params.size() >= 2) { start_time = parseStartTime(params[1]); }
        return std::unique_ptr<Pattern>(new SolidHue(hue, start_time));
    }
    // hue: What color the pulse consists off 0-255
    // startTime: control timer value to begin the pulse
    // rampDuration: ms from start of pulse to peak
    //               The time from startTime to the beginning of peak brightness
    //               at the blossom is rampDuration + TODO ms (time for the pulse)
    //               to rise up the stem.
    // peakDuration: ms to hold the flower at beak brightness
    // brightness: how bright to get 0-255
    if (patternName == "HuePulse") {
        uint8_t hue = 160;
        uint32_t startTime = parseStartTime("+0");
        uint32_t rampDuration = 300;
        uint32_t peakDuration = 600;
        uint8_t brightness = 200;
        if (params.size() >= 1) { hue = params[0].toInt(); }
        if (params.size() >= 2) { startTime = parseStartTime(params[1]); }
        if (params.size() >= 3) { rampDuration = params[2].toInt(); }
        if (params.size() >= 4) { peakDuration = params[3].toInt(); }
        if (params.size() >= 5) { brightness = params[4].toInt(); }
        return std::unique_ptr<Pattern>(new HuePulse(hue, startTime, rampDuration, peakDuration, brightness));
    }
    if (patternName == "FairyVisit") {
        uint32_t visitDuration = 3000;
        if (params.size() >= 1) { visitDuration = params[0].toInt(); }
        return std::unique_ptr<Pattern>(new FairyVisit(visitDuration));
    }
    if (patternName == "IndependentIdle") {
        return std::unique_ptr<Pattern>(new IndependentIdle());
    }
    if (patternName == "Raindrops") {
        uint8_t raindropsPerSecond = 5;
        uint32_t fadeTime = 3;
        if (params.size() >= 1) { raindropsPerSecond = params[0].toInt(); }
        if (params.size() >= 2) { fadeTime = params[1].toInt(); }
        return std::unique_ptr<Pattern>(new Raindrops(raindropsPerSecond, fadeTime));
    }
    if (patternName == "RunningDot") {
        return std::unique_ptr<Pattern>(new RunningDot());
    }
    if (patternName == "BeatFlash") {
        return std::unique_ptr<Pattern>(new BeatFlash());
    }

    comms::sendDebugMessage("Unknown LED pattern: " + patternName);
    return nullptr;
}

} // namespace led_patterns