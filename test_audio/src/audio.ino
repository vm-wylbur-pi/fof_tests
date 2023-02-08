
#include "AudioGeneratorAAC.h"
#include "AudioOutputI2S.h"
#include "AudioFileSourcePROGMEM.h"
#include "sampleaac.h"

#define Bit_Clock_BCLK 27
#define Word_Select_WS 26
#define Serial_Data_SD 25
#define GAIN 0.125

AudioFileSourcePROGMEM *in;
AudioGeneratorAAC *aac;
AudioOutputI2S *out;

void setup(){

  Serial.begin(115200);
  in = new AudioFileSourcePROGMEM(sampleaac, sizeof(sampleaac));
  aac = new AudioGeneratorAAC();
  out = new AudioOutputI2S();

  out -> SetGain(GAIN);
  out -> SetPinout(Bit_Clock_BCLK,Word_Select_WS,Serial_Data_SD);
  aac->begin(in, out);
}

void loop(){

  if (aac->isRunning()) {
            aac->loop();
  } else {
            aac -> stop();
            Serial.printf("Sound Generator\n");
            delay(1000);
  }
}

/* done */
