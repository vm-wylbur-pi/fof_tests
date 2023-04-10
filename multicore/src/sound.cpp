#include "sound.h"

#include "comms.h"
#include "music_sync.h"

// https://github.com/schreibfaul1/ESP32-audioI2S/blob/master/src/Audio.h
#include <Audio.h>

// Digital I/O used  //Makerfabs Audio V2.0
#define I2S_DOUT 27
#define I2S_BCLK 26
#define I2S_LRC 25

// Physical Buttons on the Audio board
// I think this is the button next to the 3.5 audio jack
const uint8_t PIN_VOL_UP = 39; // rock one way
const uint8_t PIN_VOL_DOWN = 36;  // rock the other way
const uint8_t PIN_MUTE = 35;      // push down in the middle.
// TODO: confirm which button is which
const uint8_t PIN_PREVIOUS = 15;
const uint8_t PIN_PAUSE = 33;
const uint8_t PIN_NEXT = 2;

namespace sound
{
    //  The main audio object
    Audio audio;

    // State variables for handling physical buttons.
    uint32_t lastButtonTimeMillis = 0;
    uint8_t volumeBeforeMuting;

    void setupAudio() {
        pinMode(PIN_VOL_UP, INPUT_PULLUP);
        pinMode(PIN_VOL_DOWN, INPUT_PULLUP);
        pinMode(PIN_MUTE, INPUT_PULLUP);
        pinMode(PIN_PREVIOUS, INPUT_PULLUP);
        pinMode(PIN_PAUSE, INPUT_PULLUP);
        pinMode(PIN_NEXT, INPUT_PULLUP);

        // TODO: experiment with more Audio parameters.
        //   - The constructor takes (bool internalDAC).
        //  - It may or may not us PSRAM, and we might care about the difference.

        // Audio(I2S)
        audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
        audio.setVolume(audio.maxVolume() / 2);

        comms::sendDebugMessage("Audio initialized");

        // TEMP: register the beat handler as a callback. If this slows down
        // FPS too much, I should hard-code it in the music sync poller instead.
        music_sync::onBeat(&beatHappened);
    }

    void mainLoop() {
        audio.loop();

        // This is where I could put code for tracking progress through
        // the current sound, notifications for when sounds finish, etc.

        // Protect against botton bounce.  This could be more sophisticated
        // if we cared, wanted to respond to held-down buttons, etc.
        bool longEnoughSinceLastButtonPress = millis() - lastButtonTimeMillis > 300;
        if (longEnoughSinceLastButtonPress) {
            if (digitalRead(PIN_VOL_DOWN) == 0)
            {
                comms::sendDebugMessage("Physical button: vol_down");
                if (audio.getVolume() > 0) {
                    audio.setVolume(audio.getVolume() - 1);
                }
                lastButtonTimeMillis = millis();
            }
            if (digitalRead(PIN_VOL_UP) == 0)
            {
                comms::sendDebugMessage("Physical button: vol_down");
                if (audio.getVolume() < audio.maxVolume()) {
                    audio.setVolume(audio.getVolume() + 1);
                }
                lastButtonTimeMillis = millis();
            }
            if (digitalRead(PIN_MUTE) == 0)
            {
                comms::sendDebugMessage("Physical button: mute");
                if (audio.getVolume() != 0) {
                    volumeBeforeMuting = audio.getVolume();
                    audio.setVolume(0);
                } else {
                    audio.setVolume(volumeBeforeMuting);
                }
                lastButtonTimeMillis = millis();
            }
        }
    }

    String formattedVolume() {
        return String(audio.getVolume()) + "/" + String(audio.maxVolume());
    }

    void beatHappened(unsigned long beatControlTime) {
        commands::playSoundFile("mono-kick-full-one-shot_110bpm_C.wav");
    }

    // These functions are generally called from the networking thread
    // after a server command is received. Dispatch is in comms.cpp
    namespace commands {
        void setVolume(uint8_t newVolume) {
            if (newVolume <= audio.maxVolume()) {
                audio.setVolume(newVolume);
            } else {
                audio.setVolume(audio.maxVolume());
            }
        }

        void playSoundFile(const String &filename) {
            bool success = audio.connecttoFS(SD, filename.c_str());
            if (!success) {
                comms::sendDebugMessage("Error playing file: " + filename);
            }
        }

        void stopSoundFile() {
            audio.stopSong();
        }

    } // namespace commands

} // namespace sound