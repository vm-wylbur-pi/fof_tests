#ifndef MUSIC_SYNC_H
#define MUSIC_SYNC_H

#include <functional>

namespace music_sync
{
    // callback once, at every beat, with the control time value at the beat.
    void onBeat(std::function<void(unsigned long)> callback);

    // To be called from an inner loop. Uses the global control timer
    // and the setBPM tempo to decide if a beat has begun since the
    // last call, and if so, runs each of the callbacks.
    void checkForBeatAndRunCallbacks();

    namespace commands {
        // Set the music BPM.  This will actually round the tempo to the nearest
        // tempo which is representable as a whole number of milliseconds.
        //   newBPM = 122 --> actual tempo = 121.95 (492 milliseconds)
        //   newBPM = 120 --> actual tempo = 120 (eactly 500 milliseconds)
        void setBPM(uint16_t newBPM);
    }

}

#endif // MUSIC_SYNC_H
