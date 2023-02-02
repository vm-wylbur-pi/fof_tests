

static int fader = 0;
static CEveryNMillis timer(20);

CRGB start = CRGB::Black;
CRGB end = CRGB::Orange;

if(fader < 256 && timer) {
    leds[0] = blend(start, end, fader);
    FastLED.show();
    fader++;
}



