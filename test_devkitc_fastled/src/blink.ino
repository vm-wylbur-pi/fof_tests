#include <FastLED.h>

// How many internal neopixels do we have? some boards have more than one!
#define NUM_LEDS 1
#define DATA_PIN 15

CRGB leds[NUM_LEDS];

// the setup routine runs once when you press reset:
void setup() {
  Serial.begin(9600);
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
}

// the loop routine runs over and over again forever:
void loop() {
  // Turn the LED on, then pause
  leds[0] = CRGB::Red;
  FastLED.show();
  FastLED.delay(500);

  // Now turn the LED off, then pause
  leds[0] = CRGB::Black;
  FastLED.show();
  FastLED.delay(500);
}
