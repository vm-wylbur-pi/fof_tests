#include "audio.h"

#include "comms.h"
#include "music_sync.h"

// https://github.com/earlephilhower/ESP8266Audio
#include "AudioFileSourceSD.h"
#include "AudioGeneratorWAV.h"
#include "AudioOutputI2S.h"

// TODO: Address click/pop issue at the start of playback.
// Based on others' experience, it's possible but requires
// a patched library, and the exact fix depends on the audio
// setup.
// https://github.com/earlephilhower/ESP8266Audio/issues/406

// Digital I/O used  //Makerfabs Audio V2.0
#define I2S_DOUT 27  // Data line. aka SD etc
#define I2S_BCLK 26  // Bit clock line. aka SCK
#define I2S_LRC 25   // Word clock line. aka WS aka FS aka LRCLK
// TODO: find out the MCLK pin for the makerfabs board, then
//       set it in the i2s constructor. Optional, but gives the
//       i2s board a reference clock that might help audio quality.

// Physical Buttons on the Audio board
// I think this is the button next to the 3.5 audio jack
const uint8_t PIN_VOL_UP = 39; // rock one way
const uint8_t PIN_VOL_DOWN = 36;  // rock the other way
const uint8_t PIN_MUTE = 35;      // push down in the middle.
// TODO: confirm which button is which
const uint8_t PIN_PREVIOUS = 15;
const uint8_t PIN_PAUSE = 33;
const uint8_t PIN_NEXT = 2;

namespace audio
{
    //  The main audio objects
    //Audio audio;
    AudioFileSourceSD *sdAudioSource = nullptr;
    AudioGeneratorWAV *wavGenerator = nullptr;
    AudioOutputI2S *i2sAudioOutput = nullptr;

    // Volume goes from 0.0 to 11.0
    float volume;
    // So we con return directly to the pre-mute volume.
    float volumeBeforeMuting;
    const float MIN_VOLUME = 0.0;
    const float MAX_VOLUME = 11.0;  // Ours go to 11.
    // Audio library's maximum Gain is 4.0, but setting to exactly 4.0
    // corresponds to uint8_t=256, which rolls over. So to avoid this
    // we need a slightly lower ceiling.
    const float MAX_GAIN = 4.0 * 255.0/256.0;

    // State variables for handling physical buttons.
    uint32_t lastButtonTimeMillis = 0;

    void setupAudio() {
        pinMode(PIN_VOL_UP, INPUT_PULLUP);
        pinMode(PIN_VOL_DOWN, INPUT_PULLUP);
        pinMode(PIN_MUTE, INPUT_PULLUP);
        pinMode(PIN_PREVIOUS, INPUT_PULLUP);
        pinMode(PIN_PAUSE, INPUT_PULLUP);
        pinMode(PIN_NEXT, INPUT_PULLUP);

        // Audio(I2S)
        sdAudioSource = new AudioFileSourceSD();
        wavGenerator = new AudioGeneratorWAV();
        i2sAudioOutput = new AudioOutputI2S();

        // params are int bclkPin, int wclkPin, int doutPin
        i2sAudioOutput->SetPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
        commands::setVolume(5.0);  // out of 11

        comms::sendDebugMessage("Audio initialized");

        // TEMP: register the beat handler as a callback. If this slows down
        // FPS too much, I should hard-code it in the music sync poller instead.
        music_sync::onBeat(&beatHappened);
    }

    void mainLoop() {
        if (wavGenerator->isRunning()) {
            if (!wavGenerator->loop()) {
                wavGenerator->stop();
            }
        }

        // This is where I could put code for tracking progress through
        // the current sound, notifications for when sounds finish, etc.

        // Protect against botton bounce.  This could be more sophisticated
        // if we cared, wanted to respond to held-down buttons, etc.
        // bool longEnoughSinceLastButtonPress = millis() - lastButtonTimeMillis > 300;
        // if (longEnoughSinceLastButtonPress) {
        //     if (digitalRead(PIN_VOL_DOWN) == 0)
        //     {
        //         comms::sendDebugMessage("Physical button: vol_down");
        //         if (audio.getVolume() > 0) {
        //             audio.setVolume(audio.getVolume() - 1);
        //         }
        //         lastButtonTimeMillis = millis();
        //     }
        //     if (digitalRead(PIN_VOL_UP) == 0)
        //     {
        //         comms::sendDebugMessage("Physical button: vol_down");
        //         if (audio.getVolume() < audio.maxVolume()) {
        //             audio.setVolume(audio.getVolume() + 1);
        //         }
        //         lastButtonTimeMillis = millis();
        //     }
        //     if (digitalRead(PIN_MUTE) == 0)
        //     {
        //         comms::sendDebugMessage("Physical button: mute");
        //         if (audio.getVolume() != 0) {
        //             volumeBeforeMuting = audio.getVolume();
        //             audio.setVolume(0);
        //         } else {
        //             audio.setVolume(volumeBeforeMuting);
        //         }
        //         lastButtonTimeMillis = millis();
        //     }
        // }
    }

    String formattedVolume() {
        const static int DECIMAL_PLACES = 1;
        return String(volume, DECIMAL_PLACES) + "/11";
    }

    void beatHappened(unsigned long beatControlTime) {
        //commands::playSoundFile("mono-kick-full-one-shot_110bpm_C.wav");
    }

    // These functions are generally called from the networking thread
    // after a server command is received. Dispatch is in comms.cpp
    namespace commands {
        void setVolume(float newVolume) {
            if (newVolume < MIN_VOLUME) newVolume = MIN_VOLUME;
            if (newVolume > MAX_VOLUME) newVolume = MAX_VOLUME;
            
            float newGain = MAX_GAIN * newVolume / MAX_VOLUME;
            i2sAudioOutput->SetGain(newGain);

            // State variable used for volume reporting and mute restoration.
            volume = newVolume;
        }

        void playSoundFile(const String &filename) {
            stopSoundFile();
            const String filePath = "/" + filename;
            if (sdAudioSource->open(filePath.c_str())) {
                wavGenerator->begin(sdAudioSource, i2sAudioOutput);
            } else {
                Serial.println("Error playing file: " + filePath);
                comms::sendDebugMessage("Error playing file: " + filePath);
            }
        }

        void stopSoundFile() {
            wavGenerator->stop();
            sdAudioSource->close();
        }

    } // namespace commands

} // namespace audio