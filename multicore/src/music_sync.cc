#include "music_sync.h"
#include "time_sync.h"
#include "comms.h"

#include <functional>
#include <vector>

namespace music_sync
{
    uint16_t millisPerBeat = 500;
    unsigned long nextBeat = 0;
    std::vector<std::function<void(unsigned long)>> beatCallbacks;

    void onBeat(std::function<void(unsigned long)> callback) {
        // Currently, no support for un-registering a callback. I wonder if we'll need it.
        beatCallbacks.push_back(callback);
    };

    // This needs to be very snappy, since it's going to be called from
    // the inner loop, probably from the LED control task.
    void checkForBeatAndRunCallbacks() {
        unsigned long controlTimer = time_sync::controlMillis();
        if (controlTimer >= nextBeat) {
            // If we want a callback structure, we can use this code. For now,
            // I'm going to keep it very simple, with a single hard-coded
            // call to the LED control object, so that this runs faster.
            for (auto callback : beatCallbacks) {
                // TODO: It's possible to pass info like beat number, or
                // start-of-bar or start-of-phrase booleans here, if we want.
                callback(nextBeat);
            }
            // Update accounting for the time needed to run the callbacks,
            // and the case where more than one beat has passed (also true for
            // the very first beat).
            nextBeat = controlTimer + millisPerBeat - (controlTimer % millisPerBeat);
        }
    }

    namespace commands
    {
        void setBPM(uint16_t newBPM){
            // millis per beat = 1000 * seconds per beat
            //                 = 1000 / (Beats/sec)
            //                 = 1000 / (BPM/60)
            //                 = 60000 / BPM
            millisPerBeat = 60000 / newBPM;
        }
    }
}