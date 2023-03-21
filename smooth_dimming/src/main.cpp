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

uint8_t gSat = 255;
uint8_t gHue = 0;
uint8_t gVal = 0;
uint8_t gMinColorStableVal = 0;  // smallest allowable value for current hue

uint8_t gBrightness = 0;
// Dimming is unstable if this is not 1; bigger values are for debugging spatial dithering
const uint8_t BRIGHTNESS_STEP_SIZE = 1;
uint8_t gDeltaBrightness = BRIGHTNESS_STEP_SIZE;

// main computed RGB based on master brightness + HSV ramp
CRGB gRGB;

const uint8_t MAX_BRIGHTNESS = 200;
// Time from max brightness to black
const uint16_t FADE_TIME_MILLIS = 2000;

// Based on observed maximum frame rate with different numbers of LEDs
// 2 for puck (41 LEDs), 3 for flower+leaves (100 LEDs)
const int MILLIS_PER_FRAME = 3;  
const int BRIGHTNESS_STEPS = MAX_BRIGHTNESS / BRIGHTNESS_STEP_SIZE;
const float MILLIS_PER_BRIGHTNESS_STEP = FADE_TIME_MILLIS / BRIGHTNESS_STEPS;
// Run the max possible spatial dithering.
const int MAX_SPATIAL_DITHER_STEPS = static_cast<int>(MILLIS_PER_BRIGHTNESS_STEP / MILLIS_PER_FRAME);
const int SPATIAL_DITHER_STEPS = min(MAX_SPATIAL_DITHER_STEPS, NUM_LEDS);
// For Spatial dithering
uint8_t gSpatialStep = 0;
// reset at each Spatial dither cycle
CRGB gRGB_prev;

// For timing the main loop
uint32_t gMicrosAtLastLoop = 0;
const uint16_t NUM_LOOP_TIMES = 1000;
uint32_t gloopTimes[NUM_LOOP_TIMES];
uint16_t gLoopTimerIndex = 0;
//   0   1   2    3  

// Lower than 2 gives noticeable color shift for some hues at low vals
// Setting to 0 shows worst color shift
const uint8_t MIN_RGB = 1;
// lower than 8 can lead to flashing when going in/out of val==0
const uint8_t MIN_DITHERING_BRIGHTNESS = 8;



// For longer string formatting
const uint8_t gPrintBuffSize = 100;
char gPrintBuff[gPrintBuffSize];

uint8_t cachedColorStableMinVals[256];


// Run once per hue, doesn't need to be fast.
uint8_t minColorStableValForHueSat(uint8_t hue, uint8_t sat) {
  uint8_t val = 255;
  CRGB rgb = CHSV(hue, sat, val);
  bool no_r = rgb.r == 0;
  bool no_g = rgb.g == 0;
  bool no_b = rgb.b == 0;
  while (   (rgb.r >= MIN_RGB || no_r) 
         && (rgb.g >= MIN_RGB || no_g)
         && (rgb.b >= MIN_RGB || no_b)
         && val > 0 )
  {
    val--;
    rgb = CHSV(hue, sat, val);
  }
  return val;
}

void printHSVtoRGBRamp(uint8_t hue, uint8_t sat) {
  CHSV hsv = CHSV(hue, sat, 0);
  CRGB rgb;
  for (uint16_t val=0; val<=255; val++) {
    hsv.v = val;
    rgb = hsv;
    snprintf(gPrintBuff, gPrintBuffSize, "%3u,%3u,%3u,%3u,%3u,%3u",
            hsv.h, hsv.s, hsv.v, rgb.r, rgb.g, rgb.b);
    Serial.println(gPrintBuff);
  }
}

void setup() {
  // 3-wire
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  // 4-wire
  //FastLED.addLeds<LED_TYPE, DATA_PIN, CLOCK_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);

  FastLED.setMaxRefreshRate(0);

  for (int hue=0; hue<=255; hue++) {
    for (uint8_t sat : {0, 128, 255}) {
      
    }
    cachedColorStableMinVals[hue] = minColorStableValForHueSat(hue, gSat);
  }

  Serial.begin(38400);
  Serial.print("setup() running on core ");
  Serial.println(xPortGetCoreID());

  gMicrosAtLastLoop = micros();

  // Serial.println("Printing in 5 seconds...");
  // delay(5000);
  // for (uint16_t hue=0; hue<=255; hue+=32) {
  //   for (uint16_t sat : {128, 255} ) {
  //     printHSVtoRGBRamp(hue, sat);
  //   }
  //   delay(10000);
  // }
}

void loop() {
  int nowMicros = micros();
  int loopMicros = nowMicros - gMicrosAtLastLoop;
  gloopTimes[gLoopTimerIndex] = loopMicros;
  gLoopTimerIndex = (gLoopTimerIndex + 1) % NUM_LOOP_TIMES;
  gMicrosAtLastLoop = nowMicros;

  if (gLoopTimerIndex == 0) {
    uint32_t sum = 0;
    for (int i=0; i<NUM_LOOP_TIMES; i++) {
      sum += gloopTimes[i];
    }
    int avgLoopTime = sum / NUM_LOOP_TIMES;
    Serial.print("avg loop() time: "); Serial.println(avgLoopTime);
  }

  EVERY_N_MILLISECONDS(static_cast<int>(MILLIS_PER_FRAME))
  {

    // STATE UPDATES
    gSpatialStep = (gSpatialStep + 1) % SPATIAL_DITHER_STEPS;

    if (gSpatialStep == 0) {
      // This block runs once for every main brightness step
      // This is where the master brightness is updated and
      // the corresponding temporal dithering and RGB is computed.

      // Update the master brightness.
      gBrightness += gDeltaBrightness;
      // Compute the corresponding RGB

      // Top of the brighten-dim pulse
      if (gBrightness >= MAX_BRIGHTNESS)
      {
        gBrightness = MAX_BRIGHTNESS;
        gDeltaBrightness = -BRIGHTNESS_STEP_SIZE;
      }

      if (gBrightness == 0)
      {
        fill_solid(leds, NUM_LEDS, CRGB(0,0,0));
        // Pause, then cycle to the next hue
        FastLED.delay(1000);
        gHue += 20;
        gMinColorStableVal = cachedColorStableMinVals[gHue];
        // For some skew hues, this is too bright
        gMinColorStableVal = min(gMinColorStableVal, static_cast<uint8_t>(30));
        //gMinColorStableVal = 0;
        gDeltaBrightness = BRIGHTNESS_STEP_SIZE;
        gSpatialStep = 0;

        // Serial.print("Hue: ");
        // Serial.print(gHue);
        // Serial.print("  min val is ");
        // Serial.println(gMinColorStableVal);

        // int brightness_steps = MAX_BRIGHTNESS / BRIGHTNESS_STEP_SIZE;
        // int steps_with_spatial_dithering = brightness_steps * SPATIAL_DITHER_STEPS;
        // int millis_per_inner_loop = FADE_TIME_MILLIS / steps_with_spatial_dithering;
        // int loop_fps = 1000 / millis_per_inner_loop;
        // Serial.print("Inner loop FPS: ");  Serial.println(loop_fps);
      }

      // Dithering brightness tracks linearly with abstract brightness,
      // but clamp it because values that are too small have too short
      // of a duty cycle even at the highest frame rate the strip can handle
      uint8_t ditheringBrightness = gBrightness;
      if (ditheringBrightness < MIN_DITHERING_BRIGHTNESS) {
        ditheringBrightness = MIN_DITHERING_BRIGHTNESS;
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
        val = 0;  // bottom out to off, so we don't linger at the floor
      }

      CHSV hsv = CHSV(gHue, gSat, val);
      gRGB_prev = gRGB;
      gRGB = hsv;
    }

    for (int i=0; i<NUM_LEDS; i++) {
      if (i % SPATIAL_DITHER_STEPS <= gSpatialStep ) {
        leds[i] = gRGB;
      } else {
        leds[i] = gRGB_prev;
      }
    }
    //fill_solid(leds, NUM_LEDS, rgb);
    

    //Serial.print(val); Serial.print(","); Serial.println(ditheringBrightness);

    // if (gDeltaBrightness = -1) {
    //   snprintf(gPrintBuff, gPrintBuffSize, "HSV: %3u,%3u,%3u    RGB: %3u,%3u,%3u   temporal dither: %3u",
    //           hsv.h, hsv.s, hsv.v, rgb.r, rgb.g, rgb.b, ditheringBrightness);
    //   Serial.println(gPrintBuff);
    // }
  }

  EVERY_N_MILLISECONDS(10000) {
    Serial.print("FPS: ");
    Serial.println(FastLED.getFPS());
    // Serial.print("millis per frame: ");
    // Serial.print(MILLIS_PER_FRAME);
    // Serial.print("  as int: ");
    // Serial.println(static_cast<int>(MILLIS_PER_FRAME));
    Serial.print("Spatial dither steps: "); Serial.println(SPATIAL_DITHER_STEPS);
  }

  // The call to show() must be outside any EVERY_N_MILLISECONDS block,
  // so that dithering can run at max FPS
  FastLED.show();
}

// EVERY_N_MILLISECONDS(20) {
//   if (gVal == 255)
//     gDeltaVal = -1;
//   if (gVal <= 1)
//     gDeltaVal = 1;
//   gVal += gDeltaVal;

//   CHSV hsv = CHSV(HUE_GREEN, 255, gVal);
//   CRGB rgb;
//   hsv2rgb_rainbow(hsv, rgb);

//   fill_solid(leds, NUM_LEDS, hsv);
//   //fill_solid(leds, NUM_LEDS, CRGB(0, 0, gVal));

//   // What's going on with the conversion?
//   char print_buf[100];
//   snprintf(print_buf, 100, "HSV: %3u,%3u,%3u    RGB: %3u,%3u,%3u   FastLED Brightness: %3u",
//            hsv.h, hsv.s, hsv.v, rgb.r, rgb.g, rgb.b, FastLED.getBrightness());
//   Serial.println(print_buf);
// FastLED.show();
// }

// Simple linear dimming using temporal dithering only.
// CHSV hsv = CHSV(HUE_GREEN, 255, 255);
// fill_solid(leds, NUM_LEDS, hsv);
// EVERY_N_MILLISECONDS(50)
// {
//   if (gBrightness == 255)
//     gDeltaBrightness = -1;
//   if (gBrightness == 0)
//     gDeltaBrightness = 1;
//   gBrightness += gDeltaBrightness;
//   FastLED.setBrightness(gBrightness);
//   FastLED.show();
// }
// EVERY_N_MILLISECONDS(500)
// {
//   Serial.print("Brightness: "); Serial.println(gBrightness);
// }

// Checking linearity of setBrightness
// EVERY_N_MILLISECONDS(1000)
// {
//   uint8_t val = brightness_combos[combo_index][0];
//   uint8_t bri = brightness_combos[combo_index][1];
//   combo_index = (combo_index + 1) % COMBO_ROWS;

//   fill_solid(leds, NUM_LEDS, CHSV(HUE_GREEN, 255, val));
//   FastLED.setBrightness(bri);

//   Serial.print("Value: ");
//   Serial.print(val);
//   Serial.print("  green: ");
//   CRGB rgb = CHSV(HUE_GREEN, 255, val);
//   Serial.print(rgb.g);
//   Serial.print("  Brightness: ");
//   Serial.println(bri);
//   Serial.print("FPS: "); Serial.println(FastLED.getFPS());
// }

// uint8_t bStep = 64;
// uint8_t valCopy = gVal;
// // The higher the current value, the smaller the dithering step.
// while (valCopy >>= 1) {
//   // For high values, it will take many bit shifts to take the val to zero.
//   // that means the brightness (dithering) step will be small. It will be zero
//   // for values in the top half of the range.
//   // For ver small values, bStep will be huge.
//   bStep >>= 1;
// }
// if (bStep > gBrightness) {
//   gBrightness = 1;
// } else {
//   gBrightness -= bStep;
// }
// Serial.print("Val: "); Serial.print(gVal);
// Serial.print("  bStep: "); Serial.print(bStep);
// Serial.print("  B: "); Serial.println(gBrightness);

// sixteen-bit brightness.
// uint16_t g16B = 0;
// bool brightening = true;

// // Test values for
// const uint8_t COMBO_ROWS = 14;
// uint8_t combo_index = 0;
// uint8_t brightness_combos[COMBO_ROWS][2] = {
//     // val, bri
//     {8, 255},
//     {8, 200},
//     {8, 128},
//     {8, 64},
//     {8, 32},
//     {8, 16},
//     {8, 8},
//     {20, 255},
//     {20, 200},
//     {20, 128},
//     {20, 64},
//     {20, 32},
//     {20, 16},
//     {20, 8}};