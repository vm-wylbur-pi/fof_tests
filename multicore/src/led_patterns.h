#ifndef LED_PATTERNS_H
#define LED_PATTERNS_H

#include <cstdint>
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
#define BLOSSOM_SIZE 60

namespace led_patterns {

// Abstract superclass for all patterns
class Pattern {
  public:
    // Evaluate the pattern, altering the content of the leds array,
    // given an absolute control timer value.
    virtual void run(uint32_t time, CRGB leds[NUM_LEDS]) = 0;
    // Returns true if the pattern was limited in time and has finished.
    // This will cause the pattern to be unloaded to free memory.
    // If this method is not overridden, the pattern will run forever.
    virtual bool isDone(uint32_t time) { return false; }
    // Should always be the subclass name. Used for polymorphism.
    virtual String name() = 0;
    // Discrption of the pattern, including parameters.
    virtual String descrip() { return name(); };
};

// Solid hue at full saturation, sent to the LEDs exactly once, at the start time.
class SolidHue : public Pattern {
  public:
    SolidHue(uint8_t hue, uint32_t start_time) : _hue(hue), _start_time(start_time) {};
    String name() { return "SolidHue"; };
    String descrip() override;
    void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
  private:
    uint8_t _hue;
    uint32_t _start_time;
};

// Full white (255,255,255) at maximum brightness (no temporal dithering).
// If this pattern is running, then led_control::setBrightness commands 
// will have no effect.
class MaxBrightnessWhite : public Pattern {
  public:
    String name() {return "MaxBrightnessWhite"; };
    void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
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

class Raindrops : public Pattern {
  public:
    Raindrops();
    // raindropsPerSecond: How often new raindrops hit the flower
    // fadeSpeed: How much brightness is removed from raindrops per update
    //            This is like the water being absorbed or flowing off the flower.
    Raindrops(uint8_t raindropsPerSecond, uint16_t fadeSpeed) :
      _raindropsPerSecond(raindropsPerSecond), _fadeSpeed(fadeSpeed) {};
    void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
    String name() {return "Raindrops";};
    String descrip() override;
  private:
    uint8_t _raindropsPerSecond;
    uint16_t _fadeSpeed;
    uint32_t _nextRaindropTime = 0;
    CRGB _leds[NUM_LEDS];
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
// fades up and down from black, so this pattern can be applied on top of an idling background.
class HuePulse : public Pattern {
  public:
    HuePulse(uint8_t hue, uint32_t startTime, uint32_t rampDuration,
             uint32_t peakDuration, uint8_t brightness)
        : _hue(hue), _startTime(startTime), _rampDuration(rampDuration),
          _peakDuration(peakDuration), _brightness(brightness){};
    void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
    bool isDone(uint32_t time) override;
    String name() {return "HuePulse";};
    String descrip() override;
  private:
    uint8_t _hue;
    uint32_t _startTime;
    uint32_t _rampDuration;
    uint32_t _peakDuration;
    uint8_t _brightness;
    fract8 _alpha[NUM_LEDS];
};

// Sets the blossom to a specified HSVA Color.
class BlossomColor : public Pattern {
  public:
    BlossomColor(CHSV color, uint8_t alpha)
      : _color(color), _alpha(alpha) {};
    void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
    String name() {return "BlossomColor";};
    String descrip() override;
  private:
    CHSV _color;
    uint8_t _alpha;
};

class FairyVisit : public Pattern {
  public:
    FairyVisit(uint32_t visitDuration, float fairySpeed)
        : _visitDuration(visitDuration), _fairySpeed(fairySpeed) {};
    void run(uint32_t time, CRGB leds[NUM_LEDS]) override;
    bool isDone(uint32_t time) override;
    String name() {return "FairyVisit";};
    String descrip() override;
  private:
    uint32_t _visitDuration;
    uint32_t _startTime = 0;
    uint32_t _lastUpdateTime = 0;
    // With respect to the LED array indexes, but the logical position of the
    // fairy can be between LEDs, to support smooth motion around the flower.
    float _fairyLocation = 70.0;
    // LEDs per second.  Positive means toward the blossom, negative toward the leaves.
    float _fairySpeed = 80.0;
};

// Construct a pattern object of the specified name and parameters.
std::unique_ptr<Pattern> makePattern(const String& patternName, const String& parameters);

}  // namespace led_patterns

#endif // LED_PATTERNS_H