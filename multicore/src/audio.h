#ifndef AUDIO_H
#define AUDIO_H

#include <Arduino.h> // For String type

namespace audio
{
    // Should be called from the main app's setup()
    void setupAudio();

    // For use with sleep mode. After calling shutdownAudio, you need to
    // call setupAudio before any calls to mainLoop() or other methods
    // in this module.
    void shutdownAudio();

    // Should be called from the main app's loop(), or a tasks forever-loop
    void mainLoop();

    // Return a string showing the current and max volume, e.g. "6/21"
    String formattedVolume();

    // Called from the music sync time polling loop once for each beat.
    void beatHappened(uint32_t beatControlTime);

    namespace commands {
        void setVolume(float newVolume);
        // filename must be a path relative to the SD card root directory.
        // startTime is absolute and checked against time_sync::controlMillis()
        // If starteTime is zero, the sound will be played right away.
        void playSoundFile(const String filename, uint32_t startTime=0);
        // Start playback of the specified sound file immediately.
        void startSoundFile(const String& filename);
        void stopSoundFile();
        // Send a listing of files in the SD card over the MQTT debug channel
        // Only includes files in the root directory.
        // Any of these files ending in .wav is probably playable.
        void listSoundFiles();

        // The audio output from wav files can be mixed with never-ending silence
        // in order to reduce the effect of stat-of-play pop. But it may cause
        // speaker hissing. This command lets us experiment with it.
        void toggleMixWithSilence();
    } // namespace commands
} // namespace audio

#endif // AUDIO_H