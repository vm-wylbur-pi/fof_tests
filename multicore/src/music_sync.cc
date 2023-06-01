#include "music_sync.h"
#include "time_sync.h"
#include "comms.h"

#include <functional>
#include <list>

namespace music_sync
{
    uint16_t millisPerBeat = 2000;
    unsigned long nextBeat = 0;
    std::list<std::function<void(unsigned long)>> beatCallbacks;

    std::_List_iterator<std::function<void(unsigned long)>> onBeat(std::function<void(unsigned long)> callback) {
        // Currently, no support for un-registering a callback. I wonder if we'll need it.
        beatCallbacks.push_front(callback);
        comms::sendDebugMessage("Registered beat callback.");
        return beatCallbacks.begin();
    };

    void unRegisterCallback(std::_List_iterator<std::function<void(unsigned long)>> callbackIteratorToRemove) {
        beatCallbacks.erase(callbackIteratorToRemove);
        comms::sendDebugMessage("Unregistered beat callback.");
    }

    // This needs to be very snappy, since it's going to be called from
    // the inner loop, probably from the LED control task.
    void checkForBeatAndRunCallbacks() {
        unsigned long controlTimer = time_sync::controlMillis();
        if (controlTimer >= nextBeat) {
            // We may need to replace with with a simple list of functions
            // but if this runs faste enough, it's cleaner.
            for (auto callback : beatCallbacks) {
                // TODO: It's possible to pass info like beat number, or
                // start-of-bar or start-of-phrase booleans here, if we want.
                callback(nextBeat);
            }
            // Update, accounting for the time needed to run the callbacks,
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