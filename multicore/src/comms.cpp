#include "comms.h"
#include "networking.h"
#include "led_control.h"

#include <Arduino.h>  // For String type

// For access to global library state for info reported in sendHeartbeat
#include <WiFi.h>
#include <FastLED.h>

namespace {
    // We must wait until Wifi is initialized before fetching the
    // MAC address. This is ensured by only calling getFlowerID
    // from the comms package, all of which is only called after
    // networking::setupWiFi.
    String flowerID = "";
    String getFlowerID() {
        if (flowerID == "") {
            // The last 3 octets of the MAC Address, colon-delimeted, e.g. AF:03:1F
            flowerID = WiFi.macAddress().substring(9);
        }
        return flowerID;
    }
}


namespace comms
{
    void sendDebugMessage(String& msg) {
        String topic = "flower-debug/" + getFlowerID();
        networking::publishMQTTMessage(topic, msg);
    }

    void sendHeartbeat() {
        // TODO: make this parseable (JSON or similar) so server can handle automatically
        String msg = "Flower heartbeat\n";
        
        msg.concat("  Flower ID: ");
        msg.concat(getFlowerID());
        msg.concat("\n");

        // I tried using the String + operator here and got weird behavior.
        msg.concat("  IP: ");
        msg.concat(WiFi.localIP().toString());
        msg.concat("\n");

        msg.concat("  WiFi Signal Strength: ");
        msg.concat(WiFi.RSSI());
        msg.concat(" dBm\n");

        msg.concat("  FastLED FPS: ");
        msg.concat(FastLED.getFPS());
        msg.concat("\n");

        String topic = "flower-heartbeats/" + getFlowerID();
        networking::publishMQTTMessage(topic, msg);
    }

    void handleMessageFromControlServer(String &topic, String &payload)
    {
        if (topic == "flower-control/leds/set_hue")
        {
            uint8_t new_hue = payload.toInt();  // Sets to zero on unconvertible string
            led_control::commands::setHue(new_hue);
            return;
        }
        // Other topics are ignored.
        Serial.println("Unhandled MQTT Message: " + topic + " - " + payload);
        sendDebugMessage("Unhandled MQTT Message: " + topic + " - " + payload);
    }
}

