#include "led_control.h"

#include <FastLED.h>

//// 4-wire LEDs
// #define NUM_LEDS 60
// #define LED_TYPE APA102
// #define DATA_PIN 23
// #define CLOCK_PIN 18
// #define COLOR_ORDER GRB

// 3-wire LEDs
#define DATA_PIN 15 // This is 13 on the board with the audio peripheral

// puck is 41, flower+leaves is about 100
#define NUM_LEDS 100

namespace led_control {

    CRGB gLEDs[NUM_LEDS];
    uint8_t gHue = 0;
    uint8_t gVal = 150;

    void setupFastLED() {
        FastLED.addLeds<NEOPIXEL, DATA_PIN>(gLEDs, NUM_LEDS);
    }

    void mainLoop() {
        gHue += 1;
        fill_solid(gLEDs, NUM_LEDS, CHSV(gHue, 255, gVal));
        FastLED.show();
        //FastLED.delay(2);

        // This turns on temporal dithering, which can only work
        // if FastLED.show() is called as often as possible.
        FastLED.setBrightness(100);

        // EVERY_N_MILLISECONDS(500) {
        //     gVal = (gVal == 20 ? 250 : 20);
        // }
    }
}