#include "util.h"

#include <Arduino.h>

#include <sstream>
#include <string>
#include <cstring>

#include "time_sync.h"

namespace util {

std::vector<String> splitString(String input, char sep) {
    std::vector<String> output;
    char *token = strtok(const_cast<char *>(input.c_str()), &sep);
    while (token != nullptr)
    {
        output.push_back(String(token));
        token = strtok(nullptr, &sep);
    }
    return output;
}

std::vector<String> splitCommaSepString(String input) {
    return splitString(input, ',');
}

uint32_t parseStartTime(const String &startTimeParameter) {
    if (startTimeParameter.startsWith("+")) {
        const uint32_t offset = startTimeParameter.substring(1).toInt();
        return time_sync::controlMillis() + offset;
    } else {
        return startTimeParameter.toInt();
    }
}

} // namespace util