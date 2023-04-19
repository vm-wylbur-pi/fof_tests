#include "comms.h"

#include "audio.h"
#include "heartbeat.h"
#include "led_control.h"
#include "networking.h"
#include "time_sync.h"
#include "music_sync.h"

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

        // I may need to move this to the LED main loop, if beats come late
        // or are skipped because of network traffic.
        music_sync::checkForBeatAndRunCallbacks();
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
        if (topic.startsWith("flower-control")) {
            // Assume that the message is intended for this flower based on
            // the MQTT subscriptions that are set up for "flower-control/all/#"
            // and "flower-control/<this flower's ID>/#"
            uint16_t firstSlash = topic.indexOf("/");
            uint16_t secondSlash = topic.indexOf("/", firstSlash+1);
            String commandName = topic.substring(secondSlash + 1);
            dispatchFlowerControlCommand(commandName, payload);
        } else {
            Serial.println("Unhandled MQTT Message: " + topic + " - " + payload);
            sendDebugMessage("Unhandled MQTT Message: " + topic + " - " + payload);
        }
    }

    void dispatchFlowerControlCommand(String &command, String &parameters) {
        // # Set a reference time
        // EVT_REFERENCE_TIME=$(date +%s)
        // /usr/local/bin/mosquitto_pub --id testclient --topic flower-control/all/time/setEventReference --message ${EVT_REFERENCE_TIME}  --retain
        // # Tell the flower to execute a flash command 4 seconds in the future.
        // COMMAND_TIME=$(echo "( $(date +%s) - ${EVT_REFERENCE_TIME} + 4) * 1000" | bc)
        // usr/local/bin/mosquitto_pub --id testclient --topic flower-control/leds/flashWhiteFiveTimesSynced --message "${COMMAND_TIME}"

        if (command == "reboot") {
            ESP.restart();
        }

        // Reference time for flower events, in seconds since unix epoch.
        if (command == "time/setEventReference") {
            unsigned long newReferenceTime = parameters.toInt();
            time_sync::commands::setEventReferenceTime(newReferenceTime);
            return;
        }
        if (command == "time/setBPM"){
            uint16_t newBPM = parameters.toInt();
            music_sync::commands::setBPM(newBPM);
            return;
        }
        if (command == "leds/toggleBeatFlashing"){
            led_control::commands::toggleBeatFlashing();
            return;
        }
        if (command == "leds/setHue") {
            uint8_t newHue = parameters.toInt();  // Sets to zero on unconvertible string
            led_control::commands::setHue(newHue);
            return;
        }
        if (command == "audio/setVolume") {
            // Range is 0.0 - 11.0.  Minimum audible volume is 0.05.
            float newVolume = parameters.toFloat();
            audio::commands::setVolume(newVolume);
            return;
        }
        if (command == "audio/playSoundFile") {
            audio::commands::playSoundFile(parameters);
            return;
        }
        if (command == "audio/stopSoundFile"){
            audio::commands::stopSoundFile();
            return;
        }
        // Other commands are ignored.
        Serial.println("Unhandled command: " + command + " - " + parameters);
        sendDebugMessage("Unhandled command: " + command + " - " + parameters);
    }
}

