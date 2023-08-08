#ifndef UTIL_H
#define UTIL_H

#include <cstdint>
#include <vector>

#include <Arduino.h> // For String type

namespace util {

    // Split string on commas and return the pieces as a vector.
    // Used for parsing parameter lists sent as bare strings over MQTT
    std::vector<String> splitCommaSepString(String str);

    // Interpret a string parameter as a moment in time. There are two formats:
    //  +1234:  Run the pattern starting 1234 milliseconds in the future.
    //  1234:   Run the pattern at absolute control time 1234.
    uint32_t parseStartTime(const String &startTimeParameter);

} // namespace util

#endif // UTIL_H