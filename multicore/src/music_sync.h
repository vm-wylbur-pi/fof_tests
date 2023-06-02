#ifndef MUSIC_SYNC_H
#define MUSIC_SYNC_H

#include <cstdint>

namespace music_sync {

class MusicBeat {
  public:
    // To be called from the inner loop of anything that wants to be beat aligned.
    // If a beat has happened since the last call to checkForBeat(), this method
    // will return the moment of the beat; otherwise it will return zero.
    uint32_t checkForBeat();
  private:
    uint32_t _nextBeat = 0;
};

namespace commands {
    // Set the music BPM.  This will actually round the tempo to the nearest
    // tempo which is representable as a whole number of milliseconds.
    //   newBPM = 122 --> actual tempo = 121.95 (492 milliseconds)
    //   newBPM = 120 --> actual tempo = 120 (eactly 500 milliseconds)
    void setBPM(uint16_t newBPM);
}

} // namespace music_sync

#endif // MUSIC_SYNC_H
