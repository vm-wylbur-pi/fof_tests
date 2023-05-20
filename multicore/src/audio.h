#ifndef AUDIO_H
#define AUDIO_H

#include <Arduino.h> // For String type

namespace audio
{
    // Should be called from the main app's setup()
    void setupAudio();

    // Should be called from the main app's loop(), or a tasks forever-loop
    void mainLoop();

    // Return a string showing the current and max volume, e.g. "6/21"
    String formattedVolume();

    // Called from the music sync time polling loop once for each beat.
    void beatHappened(unsigned long beatControlTime);

    namespace commands {
        void setVolume(float newVolume);
        // filename must be a file in the SD card root directory.
        void playSoundFile(const String& filename);
        void stopSoundFile();
        // Send a listing of files in the SD card over the MQTT debug channel
        // Any of these files ending in .wav is probably playable.
        void listSoundFiles();
    } // namespace commands
} // namespace audio

#endif // AUDIO_H