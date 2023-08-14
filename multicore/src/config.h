#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h> // For IPAddress and String type definitions

// These are values that are very likely to change between development
// environments.  They are gathered here in one file so that they're
// easy to find and modify.
namespace config {

    // Each flower is assigned to one of these SSIDs based on its sequence number. 
    const uint8_t NUM_WIFI_SSIDs = 4;
    const String SSIDs[NUM_WIFI_SSIDs] = {"Sun", "Moon", "Stars", "Comet"};
    const String PRIMARY_WIFI_PASSWORD = "fof12345"; // For the four networks here.

    // If this flower fails to connect to the SSID from SSIDs above which it is 
    // assigned to by networking::selectSSID, it will fallback to using this one.
    const String FALLBACK_SSID = "Pretty Fly for a WiFi";
    const String FALLBACK_SSID_PASSWORD = "fearandloathing";

    // This is used to configure:
    //   - the MQTT client
    //   - the NTP client
    // It must be running servers for both of these services. We should use the
    // router config to ensure that it always has this IP address.
    const IPAddress CONTROLLER_IP_ADDRESS = IPAddress(192, 168, 1, 72);

    // These need to be #defines, not consts, because of compiled optimizations in FastLED
    // Note that #define values are NOT namespace-scoped, they're just here so they can be
    // listed together with other config values.
    #define PRODUCTION_LED_DATA_PIN 13  // The custom-PCB boards ordered from China
    #define PROTOTYPE_LED_DATA_PIN 15   // The prototype boards that Patrick made.
    #define LED_DATA_PIN PRODUCTION_LED_DATA_PIN  // Referenced from led_control.cpp
}

#endif // CONFIG_H