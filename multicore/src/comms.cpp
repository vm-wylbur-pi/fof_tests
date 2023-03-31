#include "comms.h"
#include "heartbeat.h"
#include "led_control.h"
#include "networking.h"
#include "sound.h"

#include <Arduino.h>  // For String type
#include <WiFi.h> // For macAddress used in flowerID

namespace comms
{
    Heartbeat heartbeat;

    void mainLoop() {
        if (!networking::isMQTTConnected()) {
            networking::connectToMQTTBroker();
        }

        heartbeat.BeatIfItsTime();

        // Send/received any MQTT messages, and respond to received messages
        // by altering state or issuing LED control calls. If messages are
        // received, the main callback in comms.cc will dispatch.
        networking::mqttSendReceive();
    }

    String flowerID() {
        // The MAC address is not guaranteed stable until WiFi is connected.
        if (WiFi.status() != WL_CONNECTED) {
            return "ID-unavailable-WiFi-not-connected";
        }
        else {
            return WiFi.macAddress().substring(9);
        }
    }

    void sendDebugMessage(const String& msg) {
        String topic = "flower-debug/" + flowerID();
        networking::publishMQTTMessage(topic, msg);
    }

    void handleMessageFromControlServer(String &topic, String &payload) {
        if (topic == "flower-control/leds/set_hue") {
            uint8_t new_hue = payload.toInt();  // Sets to zero on unconvertible string
            led_control::commands::setHue(new_hue);
            return;
        }
        if (topic == "flower-control/audio/setVolume") {
            uint8_t newVolume = payload.toInt();
            sound::commands::setVolume(newVolume);
            return;
        }
        if (topic == "flower-control/audio/playSoundFile") {
            sound::commands::playSoundFile(payload);
            return;
        }
        if (topic == "flower-control/audio/stopSoundFile"){
            sound::commands::stopSoundFile();
            return;
        }
        // Other topics are ignored.
        Serial.println("Unhandled MQTT Message: " + topic + " - " + payload);
        sendDebugMessage("Unhandled MQTT Message: " + topic + " - " + payload);
    }
}

