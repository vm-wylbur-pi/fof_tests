#include "comms.h"
#include "networking.h"
#include "led_control.h"

#include <Arduino.h>  // For String type

// For access to global library state for info reported in sendHeartbeat
#include <WiFi.h>
#include <FastLED.h>

namespace comms
{

    void sendDebugMessage(String& msg) {
        networking::publishMQTTMessage("/flower_debug", msg);
    }

    void sendHeartbeat() {
        // TODO: make this parseable (JSON or similar) so server can handle automatically
        String msg = "Flower heartbeat\n";
        // I tried using the String + operator here and got weird behavior.
        msg.concat("  IP: ");
        msg.concat(WiFi.localIP().toString());
        msg.concat("\n");

        msg.concat("  FastLED FPS: ");
        msg.concat(FastLED.getFPS());
        msg.concat("\n");

        networking::publishMQTTMessage("/flower_heartbeats", msg);
    }

    void handleMessageFromControlServer(String &topic, String &payload)
    {
        if (topic == "/flower-control/leds/set_hue")
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

