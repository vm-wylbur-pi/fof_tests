#include "comms.h"
#include "networking.h"
#include "led_control.h"
#include "uptime.h"

#include <Arduino.h>  // For String type

// For access to global library state for info reported in sendHeartbeat
#include <WiFi.h>
#include <FastLED.h>

#define HEARTBEAT_PERIOD_MILLIS 5000

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

    Uptime uptime;
}


namespace comms
{
    uint32_t lastHeartbeatMillis = 0;

    void sendDebugMessage(String& msg) {
        String topic = "flower-debug/" + getFlowerID();
        networking::publishMQTTMessage(topic, msg);
    }

    void setupComms() {};

    void mainLoop() {
        if (!networking::isMQTTConnected()) {
            networking::connectToMQTTBroker();
        }

        // Send/received any MQTT messages, and respond to received messages
        // by altering state or issuing LED control calls. If messages are
        // received, the main callback in comms.cc will dispatch.
        networking::mqttSendReceive();

        uint32_t currentMillis = millis();
        if (currentMillis - lastHeartbeatMillis > HEARTBEAT_PERIOD_MILLIS)
        {
            Serial.println("sending heartbeat.");
            comms::sendHeartbeat();
            lastHeartbeatMillis = currentMillis;
        }
    }

    void sendHeartbeat() {
        // TODO: make this parseable (JSON or similar) so server can handle automatically
        String msg = "Flower heartbeat\n";
        
        msg += "  Flower ID: " + getFlowerID() + "\n";
        msg += "  Uptime: " + uptime.Formatted() + "\n";
        msg += "  IP: " + WiFi.localIP().toString() + "\n";
        msg += "  WiFi Signal Strength: " + networking::signalStrength() + "\n";
        msg += "  FastLED FPS: " + String(FastLED.getFPS()) + "\n";

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

