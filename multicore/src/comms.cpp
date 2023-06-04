#include "comms.h"

#include "audio.h"
#include "heartbeat.h"
#include "led_control.h"
#include "networking.h"
#include "screen.h"
#include "storage.h"
#include "time_sync.h"
#include "music_sync.h"

#include <Arduino.h>  // For String type
#include <WiFi.h> // For macAddress used in flowerID

#include <cstdint>

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

        // Handle any FTP requests.
        // Warning!! This may block for a while, resulting in interruptions of
        // other functions running in the non-LED core, including audio,
        // OTA firmware update, and MQTT.  Be careful with large file operations.
        storage::handleFTP();
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
        if (command == "reboot") {
            ESP.restart();
        }
        // Reference time for flower events, in seconds since unix epoch.
        // # This command should generally be "retained", so flowers will pick it up on reboot. 
        // EVT_REFERENCE_TIME=$(date +%s)
        // /usr/local/bin/mosquitto_pub --id testclient --topic flower-control/all/time/setEventReference --message ${EVT_REFERENCE_TIME}  --retain
        if (command == "time/setEventReference") {
            uint32_t newReferenceTime = parameters.toInt();
            time_sync::commands::setEventReferenceTime(newReferenceTime);
            return;
        }
        if (command == "time/setBPM"){
            uint16_t newBPM = parameters.toInt();
            music_sync::commands::setBPM(newBPM);
            return;
        }
        if (command == "leds/listPatterns") {
            led_control::commands::listPatterns();
            return;
        }
        if (command == "leds/clearPatterns") {
            led_control::commands::clearPatterns();
            return;
        }
        if (command.startsWith("leds/addPattern/")) {
            // Delegate parameter interpretation to the led control module, where all
            // the led patterns are defined.
            String patternName = command.substring(String("leds/addPattern/").length());
            led_control::commands::addPattern(patternName, parameters);
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
        if (command == "audio/listSoundFiles") {
            audio::commands::listSoundFiles();
            return;
        }
        if (command == "screen/setText") {
            screen::commands::setText(parameters);
            return;
        }
        if (command == "screen/appendText") {
            screen::commands::appendText(parameters);
            return;
        }
        // Other commands are ignored.
        Serial.println("Unhandled command: " + command + " - " + parameters);
        sendDebugMessage("Unhandled command: " + command + " - " + parameters);
    }
}

