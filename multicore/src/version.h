#ifndef VERSION_H
#define VERSION_H

#include <Arduino.h>

namespace version {
    // Human readable timestamp for when the firmware was compiled.
    // Format: "2023-Sep-3 10:00pm"
    String getBuildTime();

    // Name for this version of the firmware.  One version name can have
    // very many different build times.
    //
    // This is for bigger changes and helps identify important versions
    // of the flower firmware, e.g. the versions used at particular
    // events.  Generally, after you've finalized the build for each
    // named version, you should also make a git release branch for it.
    //
    // Only a name 10 characters or fewer will fit on the screen without wra
    // pping.
    //
    // "PartyTime": 2023-06-17 used at fundraising party in Patrick's backyard
    // "DressMeUp" 2023-08-08 used at the dress rehearsal
    // "NewToePaint" 2023-08-12 added NTP sync for testing
    // "FourSquare" 2023-08-14 added assigned SSID (Sun, Moon, Stars)
    // "Macbeth" 2023-08-15 MQTT reboot recovery & status sounds, improved summary screen
    //
    // Versions below (named for beaches) are versions meant for use on the playa.
    // "Venice": 2023-08-16. Add SatValPulse, leds/removePattern; remove MQTT recovery sound
    // "Muir": 2023-08-25. fix updatePattern crash bug, add startTime param to BlossomColor
    const String Name = "Muir";
}

#endif // VERSION_H