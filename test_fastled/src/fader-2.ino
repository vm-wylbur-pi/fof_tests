/*
 * File: basicfadein
 *
 * By: Andrew Tuline
 *
 * Date: April, 2019
 *
 * Based previous work (namely twinklefox) by Mark Kriegsman, this program
 * shows how you can fade-in twinkles by using the fact that a random number
 * generator with the same seed will generate the same numbers every time.
 * Combine that with millis and a sine wave and you have twinkles fading
 * in/out.
 *
 * Consider this a poor man's version of twinklefox.
 *
 */

#include <FastLED.h>

#define NUM_LEDS 48
#define LED_TYPE APA102
#define DATA_PIN 13
#define CLOCK_PIN 18
#define COLOR_ORDER GRB
#define max_bright 128

struct CRGB leds[NUM_LEDS];
int hue = 290;
uint8_t brightness = 0;
uint8_t delta;
extern const uint8_t gamma8[];

void setup() {
  LEDS.addLeds<WS2812, DATA_PIN, GRB>(leds, NUM_LEDS);  // Use this for WS2812
  // FastLED.addLeds<LED_TYPE, DATA_PIN, CLOCK_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
  FastLED.setBrightness(max_bright);
  fill_solid(leds, NUM_LEDS, CHSV(hue, 255, max_bright));
} // setup()


void loop() {
  EVERY_N_MILLISECONDS(20) {
	  basicfadein();
  }
  FastLED.show();

  EVERY_N_MILLISECONDS(1000) {
	FastLED.countFPS(100);
  	Serial.print("hue="); Serial.print(hue);
	Serial.print("; FPS="); Serial.println(FastLED.getFPS());
  }
} // loop()


void basicfadein() {
	if (brightness == 0) {
		delta = 1;
	} else if (brightness >= max_bright) {
		delta = -1;
	}
	brightness += delta;
    uint8_t b2 = pgm_read_byte(&gamma8[brightness]);
	b2 = attackDecayWave8(b2);
    fill_solid(leds, NUM_LEDS, CHSV(hue, 255, b2));
	/* FastLED.setBrightness(b2); */

} // basicfadein()


// This function is like 'triwave8', which produces a
// symmetrical up-and-down triangle sawtooth waveform, except that this
// function produces a triangle wave with a faster attack and a slower decay:
//
//     / \
//    /     \
//   /         \
//  /             \
//

uint8_t attackDecayWave8( uint8_t i)
{
  if( i < 86) {
    return i * 3;
  } else {
    i -= 86;
    return 255 - (i + (i/2));
  }
}

//---------------------------------------------------------------
// This is the gamma lookup for mapping 255 brightness levels
// The lookup table would be similar but have slightly shifted
// numbers for different gammas (gamma 2.0, 2.2, 2.5, etc.)
const uint8_t PROGMEM gamma8[] = {
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 };


// done.
