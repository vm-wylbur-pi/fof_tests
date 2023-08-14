#include "networking.h"
#include "comms.h"  // For dispatching Server commands
#include "config.h" // For Wifi name/password and the server IP address
#include "flower_info.h"
#include "screen.h"

#include <Arduino.h> // For String type.
#include <ArduinoOTA.h>
#include <WiFi.h>
// #include <ESPmDNS.h>
// #include <WiFiUdp.h>
// #include <WiFiServer.h>
#include <MQTT.h>

#include <cstdint>

namespace networking {

    // Will set the buffer size for sending and receiving.  Messages
    // exceeding this limit will fail to send.
    const uint16_t MAX_MQTT_MESSAGE_BYTES = 512;

    // Network state objects.
    WiFiClient wifi_client;
    MQTTClient mqtt_client(MAX_MQTT_MESSAGE_BYTES);

    // For throttlng OTA update progress messages
    uint32_t lastProgressUpdate = 0;

    const uint16_t WIFI_TIMEOUT_MILLIS = 5000;

    void tryToConnectToWifi(String ssid, String password) {
        WiFi.mode(WIFI_STA);
        // Workaround for library bug: https://github.com/espressif/arduino-esp32/issues/7095
        WiFi._setStatus(WL_NO_SHIELD); 
        WiFi.begin(ssid.c_str(), password.c_str());
        int status = WiFi.waitForConnectResult(WIFI_TIMEOUT_MILLIS);
        if (status != WL_CONNECTED) {
            String msg = "\nWiFi\n" + ssid + "\nfailed.\nError:\n";
            switch (WiFi.status()) {
                case WL_NO_SSID_AVAIL: msg += "SSID\nnot there"; break;
                case WL_CONNECT_FAILED: msg += "couldn't\nconnect"; break;
                default: msg += "other\nstatus=" + String(status);
            }
            screen::commands::setText(msg);
            delay(3000); // For a chance to read the failure message
        }
    };

    void setupWiFi() {
        // This will loop forever if the flower can't connect to any wifi networks.
        while(!WiFi.isConnected()) {
            tryToConnectToWifi(selectSSID(), config::PRIMARY_WIFI_PASSWORD);
            if (!WiFi.isConnected()) {
                screen::commands::setText("Trying\nfallback\nWifi\n" + 
                                          String(config::FALLBACK_SSID) + "\n");
                tryToConnectToWifi(config::FALLBACK_SSID, config::FALLBACK_SSID_PASSWORD);
                if (!WiFi.isConnected()) {
                    screen::commands::appendText("\nFallback\nfailed.\nRetrying.");
                    delay(3000);
                }
            }
        }
        screen::commands::appendText("WiFi\nConnected\n");
    };

    String selectSSID() {
        uint8_t flower_num = flower_info::flowerInfo().sequenceNum;
        // Flower numbers range from 1 to about 165, without many gaps. This
        // makes a good hashing domain.  If this is a new flower without an
        // inventory entry, we get -1, which will give the last SSID in the list.
        return config::SSIDs[flower_num % config::NUM_WIFI_SSIDs];
    }

    void setupOTA() {
        // Port defaults to 3232
        // ArduinoOTA.setPort(3232);

        // Hostname defaults to esp3232-[MAC]
        // ArduinoOTA.setHostname("myesp32");

        // No authentication by default
        // ArduinoOTA.setPassword("admin");

        // Password can be set with it's md5 value as well
        // MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
        // ArduinoOTA.setPasswordHash("21232f297a57a5a743894a0e4a801fc3");

        ArduinoOTA
        .onStart([]()
        {
            String type;
            if (ArduinoOTA.getCommand() == U_FLASH)
                type = "sketch";
            else // U_SPIFFS
                type = "filesystem";

            // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
            Serial.println("Start updating " + type);
            comms::sendDebugMessage("Receiving OTA update.");
            screen::commands::setText("Receiving OTA update.\n");
        })
        .onEnd([]()
        {
            Serial.println("\nEnd");
            comms::sendDebugMessage("OTA Update complete.  Rebooting...");
            screen::commands::appendText("OTA Update complete.  Rebooting...");
        })
        .onProgress([](uint32_t progress, uint32_t total)
        {
            // Echoing the progress to the screen on every call slows down OTA a lot,
            // so only do it every couple of secodns.
            if (millis() > lastProgressUpdate + 2000) {
                Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
                screen::commands::setText("OTA progress: \n" + String(progress) + "/" + String(total) + "\n");
                lastProgressUpdate = millis();
            }
        })
        .onError([](ota_error_t error)
        {
            Serial.printf("Error[%u]: ", error);
            if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
            else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
            else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
            else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
            else if (error == OTA_END_ERROR) Serial.println("End Failed");
        });

        ArduinoOTA.begin();
    }

    void checkForOTAUpdate() {
        ArduinoOTA.handle();
    }

    void setupMQTT() {
        mqtt_client.begin(config::CONTROLLER_IP_ADDRESS, wifi_client);
        mqtt_client.onMessage(comms::handleMessageFromControlServer);
        connectToMQTTBroker();
    }

    void connectToMQTTBroker() {
        String mqttAttemptMessage = "connecting to MQTT...\n";
        Serial.print(mqttAttemptMessage);
        screen::commands::appendText(mqttAttemptMessage);

        String client_name = "flower-" + flower_info::flowerID();
        // connect() is where we can supply username/password if we want.
        uint8_t num_attempts = 0;
        while (!mqtt_client.connected() && num_attempts++ <= 3) {
            Serial.print(".");
            mqtt_client.connect(client_name.c_str());
            delay(1000);
        }
        if (mqtt_client.connected()) {
            Serial.println("\nconnected!");
            screen::commands::appendText("MQTT connected\n");
            // Main communication channel into the flower
            // Control commands directed at all flowers.
            mqtt_client.subscribe("flower-control/all/#");
            // Control commands directed at just this flower.
            mqtt_client.subscribe("flower-control/" + flower_info::flowerID() + "/#");
            mqtt_client.subscribe("flower-control/" + String(flower_info::flowerInfo().sequenceNum) + "/#");
        } else {
            String mqttFailureMessage = "\nFailed to connect to MQTT broker at\n"
                + config::CONTROLLER_IP_ADDRESS.toString() + "\n";
            Serial.println(mqttFailureMessage);
            screen::commands::setText(mqttFailureMessage);
        }
    }

    bool isMQTTConnected() {
        return mqtt_client.connected();
    }

    void publishMQTTMessage(const String& topic, const String& payload) {
        if (mqtt_client.connected()) {
            bool success = mqtt_client.publish(topic, payload);
            if (!success) {
                Serial.println("Failed to publish MQTT message in " + topic);
            }
        }
    }

    void mqttSendReceive() {
        // send and receive any pending MQTT packets. If new data is received
        // this will lead to handleMQTTMessage being called
        mqtt_client.loop();
    }

    String signalStrength() {
        int16_t strength = WiFi.RSSI();
        String descrip;
        if      (strength > -30) {descrip = "Unbelievable";}
        else if (strength > -50) {descrip = "Excellent";}
        else if (strength > -60) {descrip = "Good";}
        else if (strength > -67) {descrip = "OK";}
        else if (strength > -70) {descrip = "Bad";}
        else if (strength > -80) {descrip = "Very Bad";}
        else if (strength > -90) {descrip = "Awful";}
        else                     {descrip = "Unusuable";}
        return String(strength) + " dBm (" + descrip + ")";
    }

}  // namespace networking;