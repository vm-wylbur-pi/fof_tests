#include "util.h"

#include <Arduino.h>

#include <sstream>
#include <string>
#include <cstring>

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

} // namespace util