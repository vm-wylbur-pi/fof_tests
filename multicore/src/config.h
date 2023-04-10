#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h> // For IPAddress and String type definitions

// These are values that are very likely to change between development
// environments.  They are gathered here in one file so that they're
// easy to find and modify.
namespace config {

    // Name and password for the wifi. Modify this in your local copy
    // of the file, but don't commit, until we're working with the
    // deployment router.
    const String WIFI_SSID = "FILL_ME_IN";
    const String WIFI_PASSWORD = "FILL_ME_IN";

    // This is used to configure:
    //   - the MQTT client
    //   - the NTP client
    // It must be running servers for both of these services. We should use the
    // router config to ensure that it always has this IP address.
    const IPAddress CONTROLLER_IP_ADDRESS = IPAddress(192, 168, 1, 72);

}

#endif // CONFIG_H