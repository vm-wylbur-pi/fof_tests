#include "music_sync.h"
#include "time_sync.h"

namespace music_sync {

// This is a global, referenced by all instances of MusicBeat, and maybe later
// other code.  For safety, it shouldn't be directly set; instead call
// music_sync::commands::setBPM.
uint16_t millisPerBeat = 1300;  // arbitrary default, slow andante

uint32_t MusicBeat::checkForBeat() {
    uint32_t controlTimer = time_sync::controlMillis();
    if (controlTimer >= _nextBeat) {
        uint32_t beatTime = _nextBeat;
        // Update, accounting for the the case where more than one beat has
        // passed (also true for the very first beat).
        // The values of controlTimer and millisPerBeat will be the same across
        // all flowers, which is how we get field-wide beat alignment.
        _nextBeat = controlTimer + millisPerBeat - (controlTimer % millisPerBeat);

        return beatTime;
    } else {
        // No new beat since the last call
        return 0;
    }
}

namespace commands {
    void setBPM(uint16_t newBPM){
        // millis per beat = 1000 * seconds per beat
        //                 = 1000 / (Beats/sec)
        //                 = 1000 / (BPM/60)
        //                 = 60000 / BPM
        millisPerBeat = 60000 / newBPM;
    }
}

}