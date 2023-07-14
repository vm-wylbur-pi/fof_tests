#include "audio.h"

#include "comms.h"
#include "music_sync.h"
#include "screen.h"
#include "storage.h"

// https://github.com/earlephilhower/ESP8266Audio
#include "AudioFileSourceSD.h"
#include "AudioFileSourceFunction.h"
#include "AudioGeneratorWAV.h"
#include "AudioOutputI2S.h"
#include "AudioOutputMixer.h"

#include <cstdint>

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

namespace audio
{
    //  The main audio objects.
    //
    // Audio Input (WAV-file data from the SD card)
    AudioFileSourceSD *sdAudioSource = nullptr;
    AudioGeneratorWAV *wavGenerator = nullptr;
    // When the input is WAV-data only, there is an audible pop at the beginning of
    // playback. To avoid this, we have a 2nd input which generates continuous
    // silence, we mix the silence with the WAV data, and send it to the output.
    // This means sound is always flower, so the pop happens once on audio initializiton,
    // instead of every time we play a new WAV file.
    AudioFileSourceFunction *silenceSource = nullptr;
    AudioGeneratorWAV *silenceGenerator = nullptr;

    // Mixing.  The mixer takes the data from wavGenerater (which starts and stops) and
    // the data from silenceGenerator, and combines them, sending the mix to i2sAudioOutput
    AudioOutputMixer *mixer;
    AudioOutputMixerStub *wavMixerStub;
    AudioOutputMixerStub *silenceMixerStub;

    // Audio Output (sent over the I2S bus to the audio shield)
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

    void setupAudio() {
        // Audio Input (WAV-file data from the SD card)
        sdAudioSource = new AudioFileSourceSD();
        wavGenerator = new AudioGeneratorWAV();

        // Silence Generator (2nd input, will be mixed with the WAV data)
        // See https://github.com/earlephilhower/ESP8266Audio/blob/master/examples/PlayWAVFromFunction/PlayWAVFromFunction.ino
        silenceSource = new AudioFileSourceFunction(
            10.0,  // Duration of audio in seconds.
            1,     // num channels. 1=mono
            8000,  // sample rate in hz. Minimum, since this need to be high for silence. :)
            16     // bits/sample
        );
        // Define the function the specifies the silence audio.  Only one function is needed for mono.
        silenceSource->addAudioGenerators([&](const float time) {
            // Expected amplitude return is between -1.f and +1.f. 
            // Constant zero is detected by the DAC as "silence", causing it to shut off,
            // so return a non-zero constant.
            return 1;
         });
        // Data from the silenceSource is used by silenceGenerator (all sound sources are Generators)
        silenceGenerator = new AudioGeneratorWAV();

        // Audio Output
        i2sAudioOutput = new AudioOutputI2S();
        // params are int bclkPin, int wclkPin, int doutPin
        i2sAudioOutput->SetPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);

        // Set up mixing of wav data with Silence
        // See https://github.com/earlephilhower/ESP8266Audio/blob/master/examples/MixerSample/MixerSample.ino
        mixer = new AudioOutputMixer(32, i2sAudioOutput);   // 32 is the mixer buffsize, copied from example.
        wavMixerStub = mixer->NewInput();
        silenceMixerStub = mixer->NewInput();

        commands::setVolume(5.0);  // out of 11

        comms::sendDebugMessage("Audio initialized");
        screen::commands::appendText("Audio initialized");
    }

    void mainLoop() {
        if (wavGenerator->isRunning()) {
            if (!wavGenerator->loop()) {
                wavGenerator->stop();  // TODO: Try without this. Maybe this isn't needed anymore?
                wavMixerStub->stop();
            }
        }

        // Monitor the silence Generator. If it gets near its logical end (it's
        // configured with a finite duration), then seek back to its beginning.
        // Thus the silence never ends.
        if (silenceGenerator->isRunning()) {
            silenceGenerator->loop();
            if (silenceSource->getPos() > silenceSource->getSize() > 0.5) {
                comms::sendDebugMessage("looping silence");
                silenceSource->seek(0, SEEK_SET);
            } 
        }

        // This is where I could put code for tracking progress through
        // the current sound, notifications for when sounds finish, etc.
    }

    void shutdownAudio() {
        commands::stopSoundFile();
        silenceGenerator->stop();
        silenceMixerStub->stop();
        i2sAudioOutput->stop();
    }

    String formattedVolume() {
        const static int DECIMAL_PLACES = 1;
        return String(volume, DECIMAL_PLACES) + "/11";
    }

    void beatHappened(uint32_t beatControlTime) {
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
                wavGenerator->begin(sdAudioSource, wavMixerStub);
            } else {
                Serial.println("Error playing file: " + filePath);
                comms::sendDebugMessage("Error playing file: " + filePath);
            }
        }

        void stopSoundFile() {
            wavGenerator->stop();
            wavMixerStub->stop();
            sdAudioSource->close();
        }

        void listSoundFiles() {
            String fileListDebugMsg = "SD Card Root directory contents\n";
            String fileNames[30];
            int num_files = storage::listFilesInRootDir(fileNames);
            fileListDebugMsg += "  " + String(num_files) + " files\n";
            if (num_files > 30) {
                int numNotShown = num_files - 30;
                fileListDebugMsg += " WARNING! Only the first 30 files are listed.\n "
                                    + String(numNotShown) + " files are not shown.";
                num_files = 30;
            }
            for (uint16_t i = 0; i < num_files; i++) {
                fileListDebugMsg += fileNames[i];
                fileListDebugMsg += "\n";
            }
            Serial.println(fileListDebugMsg);
            comms::sendDebugMessage(fileListDebugMsg);
        }

        void toggleMixWithSilence() {
            if (silenceGenerator->isRunning()) {
                silenceGenerator->stop();
                silenceMixerStub->stop();
            } else {
                silenceGenerator->begin(silenceSource, silenceMixerStub);
            }
            comms::sendDebugMessage("silenceGenerator isRunning: "+ String(silenceGenerator->isRunning()));
        }

    } // namespace commands

} // namespace audio