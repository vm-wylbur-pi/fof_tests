#include "comms.h"

#include "audio.h"
#include "buttons.h"
#include "flower_info.h"
#include "heartbeat.h"
#include "led_control.h"
#include "networking.h"
#include "screen.h"
#include "sleep.h"
#include "storage.h"
#include "time_sync.h"
#include "util.h"
#include "music_sync.h"

#include <Arduino.h>  // For String type

#include <cstdint>

namespace comms
{
    Heartbeat heartbeat;

    void mainLoop() {
        if (!networking::isMQTTConnected()) {
            networking::connectToMQTTBroker();
        }

        heartbeat.BeatIfItsTime();

        // Handle physical button pushes on the side of the flower circuit board
        buttons::mainLoop();

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

    void forceHeartbeat() {
        heartbeat.Beat();
    }

    void sendDebugMessage(const String& msg) {
        String topic = "flower-debug/" + flower_info::flowerID();
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
        if (command == "enterSleepMode") {
            // Default to sleeping for 10 seconds. This is relatively short, to make
            // recovery fast during testing and accidental use. 
            uint32_t millisToSleep = 10 * 1000;
            if (parameters != "") {
                // Parameter parse failure will result in a sleep time of zero.
                millisToSleep = parameters.toInt();
            }
            sleep_mode::commands::enterDeepSleep(millisToSleep);
        }
        if (command == "time/syncWithNTP") {
            time_sync::commands::syncWithNTP();
            return;
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
        if (command.startsWith("leds/updatePattern/")) {
            // Delegate parameter interpretation to the led control module, where all
            // the led patterns are defined.
            String patternName = command.substring(String("leds/updatePattern/").length());
            led_control::commands::updatePattern(patternName, parameters);
            return;
        }
        if (command == "leds/setBrightness") {
            uint8_t newBrightness = led_control::DEFAULT_BRIGHTNESS;
            if (parameters != "") {
                newBrightness = parameters.toInt();
            }
            led_control::commands::setBrightness(newBrightness);
            return;
        }
        if (command == "audio/setVolume") {
            // Range is 0.0 - 11.0.  Minimum audible volume is 0.05.
            float newVolume = parameters.toFloat();
            audio::commands::setVolume(newVolume);
            return;
        }
        if (command == "audio/playSoundFile") {
            std::vector<String> params = util::splitCommaSepString(parameters);
            String fileName = "";
            uint32_t startTime = util::parseStartTime("+0");  // Default is play right away.            
            if (params.size() >= 1) { fileName = params[0]; }
            if (params.size() >= 2) { startTime = util::parseStartTime(params[1]); }
            audio::commands::playSoundFile(fileName, startTime);
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
        if (command == "audio/toggleMixWithSilence") {
            audio::commands::toggleMixWithSilence();
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
        if (command == "screen/resetToFlowerSummary") {
            screen::commands::resetToFlowerSummary();
            return;
        }
        // Other commands are ignored.
        Serial.println("Unhandled command: " + command + " - " + parameters);
        sendDebugMessage("Unhandled command: " + command + " - " + parameters);
    }
}

