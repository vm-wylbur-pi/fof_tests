#include <Arduino.h>
#include <FastLED.h>

//// 4-wire LEDs
// #define NUM_LEDS 60
// #define LED_TYPE APA102
// #define DATA_PIN 23
// #define CLOCK_PIN 18
// #define COLOR_ORDER GRB

// 3-wire LEDs
#define DATA_PIN 15   // This is 13 on the board with the audio peripheral

// puck is 41, flower+leaves is about 100
#define NUM_LEDS 100
CRGB leds[NUM_LEDS];

// CONSTANTS
////////////////////////////////////////////////////////////////
// Where to start the color ramp.
// 255 shows the full brightness range of the LEDs, but nothing interesting for the
// smooth dimming problem happens above 128. You might need this to be higher if
// you're in a bright room.
const uint8_t MAX_BRIGHTNESS = 200;
// Dimming is unstable if this is not 1; bigger values are for debugging spatial dithering
const uint8_t BRIGHTNESS_STEP_SIZE = 1;
// Time from max brightness to black.  Set higher to notice more stutter.
const uint16_t DIMMING_TIME_MILLIS = 2000;
const int BRIGHTNESS_STEPS = MAX_BRIGHTNESS / BRIGHTNESS_STEP_SIZE;
const float MILLIS_PER_BRIGHTNESS_STEP = DIMMING_TIME_MILLIS / BRIGHTNESS_STEPS;
// Based on observed maximum frame rate with different numbers of LEDs
// 2 for puck (41 LEDs), 3 for flower+leaves (100 LEDs)
const int MILLIS_PER_FRAME = 3;
const int MAX_SPATIAL_DITHER_STEPS = static_cast<int>(MILLIS_PER_BRIGHTNESS_STEP / MILLIS_PER_FRAME);
// You can't have more spatial dither steps than you have LEDs.  This only matters
// at very long dimming times, when you spend a long time at each brightness step.
const int SPATIAL_DITHER_STEPS = min(MAX_SPATIAL_DITHER_STEPS, NUM_LEDS);
// Lower limit Limit on each RGB component  when it is in a color mix with other components.
// Lower than 2 gives noticeable color shift for some hues at low vals, due to discretization
// of components causes a shift in component ratios.
// 1 is an acceptable compromise between a little color shift and a lower min val, to get
// a smoother transition to black.
// Setting to 0 shows the worst color shift
const uint8_t MIN_RGB = 1;
// Temporal dithering duty cycle, as a fraction of 255.
// lower than 8 can lead to flashing artifacts when going in/out of val==0
const uint8_t MIN_TEMPORAL_DITHERING_BRIGHTNESS = 8;

// State variables referenced from inside loop()
/////////////////////////////////////////////////////
// Main state variable for dimming.  "abstract" brightness.
// hsv.v and FastLED.setBrightness() are functions of this.
// Ranges from zero to MAX_BRIGHTNESS
uint8_t gBrightness = 0;
// Spatial dithering state variable. Ranges from 1 to MAX_SPATIAL_DITHER_STEPS (incremented on first use)
uint8_t gSpatialStep = 0;
// HSV corresponding to the current gBrightness
uint8_t gSat = 255;
uint8_t gHue = 0;
uint8_t gVal = 0;
// RGB corresponding to gSat,gHue,gVal
CRGB gRGB;
// The value of gRGB before the most recent change in gBrightness.
// Spatial dithering chooses between gRGB and gRGB_prev for each LED.
CRGB gRGB_prev;

// Smallest HSV.v value to use at the current Hue+Sat.  Any smaller would cause
// collor shift, so if the brightness ramp calls for a lower value, we instead
// drop straight to black.
uint8_t gMinColorStableVal = 0;
// For storing pre-computed results of minColorStableValForHueSat
uint8_t cachedColorStableMinVals[256];

// How much to change brightness on each step.
// The time taken for each of these steps depends on DIMMING_TIME_MILLIS and MAX_BRIGHTNESS
uint8_t gDeltaBrightness = BRIGHTNESS_STEP_SIZE;

// Run during initialization, doesn't need to be fast.
uint8_t minColorStableValForHueSat(uint8_t hue, uint8_t sat) {
  uint8_t val = 255;
  CRGB rgb = CHSV(hue, sat, val);
  // If a given component is not involved in this hue (e.g. There's no red
  // in cyan), then we don't have to care when it gets too small.
  bool no_r = rgb.r == 0;
  bool no_g = rgb.g == 0;
  bool no_b = rgb.b == 0;
  // Check all values, decreasing from the max, until we get one that is
  // not acceptable.
  while (   (rgb.r >= MIN_RGB || no_r) 
         && (rgb.g >= MIN_RGB || no_g)
         && (rgb.b >= MIN_RGB || no_b)
         && val > 0 )
  {
    val--;
    rgb = CHSV(hue, sat, val);
  }
  // If we fell through the loop because val got to zero, then that's fine
  // This is for hues that only use one component (e.g. hue=0 pure saturated red) or 
  // hues that have equal amounts of all involved components (e.g. white or cyan).
  if (val==0) {
    return 0;
  } else {
    // We failed one of the component >MIN_RGB conditions.  The current value of val
    // is the one that failed, so the previous value is the minimal good one.
    return val+1;
  }
}

void setup() {
  // 3-wire LED strand
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  // 4-wire LED strand
  //FastLED.addLeds<LED_TYPE, DATA_PIN, CLOCK_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);

  // No FPS limit
  FastLED.setMaxRefreshRate(0);

  // Pre-compute a lookup table for how dim you can make each hue
  // before you start to notice color shifting.
  for (int hue=0; hue<=255; hue++) {
    cachedColorStableMinVals[hue] = minColorStableValForHueSat(hue, gSat);
  }

  Serial.begin(38400);
}

void loop() {
  EVERY_N_MILLISECONDS(MILLIS_PER_FRAME)
  {
    // This is the inner loop, running once for each frame. For each
    // value of gBrightness, this runs SPATIAL_DITHER_STEPS times.
    // The first value of gSpatialStep for each gBrightness is 1.
    gSpatialStep = (gSpatialStep + 1) % SPATIAL_DITHER_STEPS;

    if (gSpatialStep == 0) {
      // This block runs once for every main brightness step (the "outer" loop)
      // This is where the master brightness is updated and
      // the corresponding temporal dithering and RGB is computed.

      // Update the master brightness.
      gBrightness += gDeltaBrightness;

      // Top of the brighten-dim pulse, switch from brightening to dimming
      if (gBrightness >= MAX_BRIGHTNESS) {
        gBrightness = MAX_BRIGHTNESS;
        gDeltaBrightness = -BRIGHTNESS_STEP_SIZE;
      }

      if (gBrightness == 0) {
        // Special handling upon reaching zero brightness (black), zero
        // everything to cover any linger spatial dithering.
        fill_solid(leds, NUM_LEDS, CRGB(0,0,0));

        // Pause at black, then cycle to the next hue
        FastLED.delay(1000);
        // Increment enough to get through a variety of hues in not too much time
        // Not having this be a power of 2 means you get different hues after
        // rolling over.
        gHue += 20;
        // After the pause we need to brighten again.
        gDeltaBrightness = BRIGHTNESS_STEP_SIZE;

        // Look up the minimum color-stable value for the new hue. This will
        // be the floor val for the dim.
        gMinColorStableVal = cachedColorStableMinVals[gHue];

        // For some hues with high RGB skew (high ratios of R:G, R:B, or G:B), the
        // min val is too high, and gives a noticeable jump from medium brightness
        // all the way to black. This is a limit on that effect that tolerates a bit
        // of color shift for the sake of avoiding that jump.
        gMinColorStableVal = min(gMinColorStableVal, static_cast<uint8_t>(30));

        // Uncomment if you want to see the color shift
        //gMinColorStableVal = 0;

        // Reset inner loop counter; we may have finished getting to black
        // partway through a spatial dither progression.
        gSpatialStep = 0;
      }

      // Temporal dithering brightness tracks linearly with abstract brightness,
      // but clamp it because values that are too small have too short
      // of a duty cycle even at the highest frame rate the strip can handle
      uint8_t ditheringBrightness = gBrightness;
      if (ditheringBrightness < MIN_TEMPORAL_DITHERING_BRIGHTNESS) {
        ditheringBrightness = MIN_TEMPORAL_DITHERING_BRIGHTNESS;
      }
      FastLED.setBrightness(ditheringBrightness);

      uint8_t val;
      if (gBrightness >= gMinColorStableVal) {
        // HSV Value tracks abstract brightness linearly. This results
        // in a nice gamma correction: one step of V corresponds to
        // several steps of RGB at high V, and it takes several steps
        // of V to correspond to one step of RGB at the lowest brightness.
        val = gBrightness;
      } else {
        // Avoid low but non-zero values which cause color shifts.
        val = 0;
      }

      CHSV hsv = CHSV(gHue, gSat, val);
      gRGB_prev = gRGB;
      gRGB = hsv;  // implicit hsv->rgb conversion
    } // end of per-brightness-level code

    // Spatial dithering fill
    for (int i=0; i<NUM_LEDS; i++) {
      if (i % SPATIAL_DITHER_STEPS <= gSpatialStep ) {
        leds[i] = gRGB;
      } else {
        leds[i] = gRGB_prev;
      }
    }
  } // end of per-frame code

  EVERY_N_MILLISECONDS(10000) {
    Serial.print("FPS: ");
    Serial.println(FastLED.getFPS());
    Serial.print("Spatial dither steps: "); Serial.println(SPATIAL_DITHER_STEPS);
  }

  // The call to show() must be at the top level of loop(),
  // outside any EVERY_N_MILLISECONDS block, so that temproal
  // dithering can run at max FPS
  FastLED.show();
}
