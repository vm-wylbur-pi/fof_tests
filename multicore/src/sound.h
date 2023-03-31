// I would have named tihs file audio.h, except that conflicts with the
// installed library Audio.h

#ifndef SOUND_H
#define SOUND_H

#include <Arduino.h>
#include <Audio.h>

namespace sound
{
    // Should be called from the main app's setup()
    void setupAudio();

    // Should be called from the main app's loop(), or a tasks forever-loop
    void mainLoop();

    // Return a string showing the current and max volume, e.g. "6/21"
    String formattedVolume();

    namespace commands {
        void setVolume(uint8_t newVolume);
        // filename must be a file in the SD card root directory.
        void playSoundFile(const String& filename);
        void stopSoundFile();
    } // namespace commands
} // namespace audio

#endif // SOUND_H