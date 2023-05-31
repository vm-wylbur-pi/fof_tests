#ifndef UTIL_H
#define UTIL_H

#include <vector>

#include <Arduino.h> // For String type

namespace util {

    // Split string on commas and return the pieces as a vector.
    // Used for parsing parameter lists sent as bare strings over MQTT
    std::vector<String> splitCommaSepString(String str);

} // namespace util

#endif // UTIL_H