#ifndef UTIL_H
#define FLOWER_INFO_H

#include <cstdint>
#include <vector>

#include <Arduino.h> // For String type

// This enum is defined at the top level (not in a namespace) so that the values in it
// can be referred to without qualification in the copied inventory in flower_info.cpp.
enum Species {
    unknown,
    poppy,
    geranium,
    aster
};

namespace flower_info {

    struct FlowerInfo {
        int16_t sequenceNum;  // positive integer, painted on the outside of the flower birdhouse
        String id;            // last three octets of the MAC address, e.g. "3C:80:A3"
        Species species;      // shape of the resin-cast blossom on the top of the flower
        float height;         // height of the flower in inches.  -1 means unknown (go measure it for the inventory!)
    };

    // Unique identifier for this flower, last 3 octets of the MAC address.
    // This function only works after WiFi is initialized.
    String flowerID();

    // Get all flower info for this flawer, based on flowerID.
    // This is based on compiling the flower inventory into the firmware;
    // see flower_info.cpp for details.
    FlowerInfo flowerInfo();

    // Return a formatted string used for showing a summary of the flower's
    // identity and status on the esp32 screen, in vertical orientatin.
    // Example
    //    I'm # 103
    //    FO:6D:8C
    //    poppy
    //
    //    FourSquare
    //    Built
    //    2023-08-15 12:38 PM
    //
    //    Stars
    //    MQTT OK
    String summaryForScreen();

} // namespace util

#endif // FLOWER_INFO_H