//***************************************************************
// Fade up and down using fadeToBlackBy().
//
// Showing how fadeToBlackBy can also be used to fade up from
// black to colors.  Maybe less common to do it this way, but
// it's an option.
//
// Marc Miller, Oct 2021
// https://github.com/marmilicious/FastLED_examples/blob/master/fadeToBlackBy_example2.ino
//***************************************************************


#include "FastLED.h"
#define DATA_PIN    23
#define CLOCK_PIN   18
#define LED_TYPE    APA102
#define COLOR_ORDER RGB
#define NUM_LEDS    32
#define BRIGHTNESS  255
CRGB leds[NUM_LEDS];


//---------------------------------------------------------------
void setup() {
  Serial.begin(9600);  // Allows serial monitor output
  delay(1500); // startup delay
  FastLED.addLeds<LED_TYPE,DATA_PIN,CLOCK_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.clear();
  FastLED.show();
  Serial.println("\nSetup done. \n");
}


//---------------------------------------------------------------
void loop() {
  static uint8_t STATE = 1;  // starting State
  static uint8_t fadeAmount = 0;  // current fade amount
  static unsigned long previousMillis;
  static uint8_t startHue;

  EVERY_N_MILLISECONDS(30) {
    startHue++;
  }

  EVERY_N_MILLISECONDS(50) {
    switch (STATE) {
    case 1:
      {
        fadeAmount++;  // fading out
        if (fadeAmount == 255) {
          STATE = 2;
          previousMillis = millis();
        }
      }
      break;
    case 2:
      {
        if (millis() - previousMillis > 1600) {
          STATE = 3;
        }
      }
      break;
    case 3:
      {
        fadeAmount--;  // fading in
        if (fadeAmount == 0) {
          STATE = 4;
          previousMillis = millis();
        }
      }
      break;
    case 4:
      {
        if (millis() - previousMillis > 1000) {
          STATE = 1;
        }
      }
      break;
    default:
      break;
    }
    //Serial.println(fadeAmount);
  }

  fill_rainbow(leds, NUM_LEDS, startHue, NUM_LEDS/2);
  for (uint8_t i = 0; i < NUM_LEDS/2; i++) {
    leds[i].fadeToBlackBy(fadeAmount);
  }

  FastLED.show();
  EVERY_N_MILLISECONDS(2000) {
	FastLED.countFPS(100);
  	Serial.println(FastLED.getFPS());
  }

}

