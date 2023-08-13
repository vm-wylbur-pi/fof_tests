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
    // "PartyTime" for the version used at the fundraising party in
    // Patrick's backyord on 2023-06-17.
    //
    // "DressMeUp" for the version used at the dress rehearsal on 2023-08-08
    //
    // "NewToePaint": added NTP sync for testing on 2023-08-12
    const String Name = "NewToePaint";
}

#endif // VERSION_H