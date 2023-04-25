#include "networking.h"
#include "comms.h"  // For dispatching Server commands
#include "config.h" // For Wifi name/password and the server IP address
#include "screen.h"

#include <Arduino.h> // For String type.
#include <ArduinoOTA.h>
#include <WiFi.h>
// #include <ESPmDNS.h>
// #include <WiFiUdp.h>
// #include <WiFiServer.h>
#include <MQTT.h>

namespace networking {

    // Will set the buffer size for sending and receiving.  Messages
    // exceeding this limit will fail to send.
    const uint16_t MAX_MQTT_MESSAGE_BYTES = 512;

    // Network state objects.
    WiFiClient wifi_client;
    MQTTClient mqtt_client(MAX_MQTT_MESSAGE_BYTES);

    // For throttlng OTA update progress messages
    unsigned long lastProgressUpdate = 0;

    void setupWiFi() {
        Serial.println("Connecting to WiFi (" + config::WIFI_SSID + ")");
        WiFi.mode(WIFI_STA);
        WiFi.begin(config::WIFI_SSID.c_str(), config::WIFI_PASSWORD.c_str());
        while (WiFi.waitForConnectResult() != WL_CONNECTED) {
            String failure_message = "WiFi Connection to\n" + config::WIFI_SSID + "failed.\nRebooting in 5 sec.";
            Serial.println(failure_message);
            screen::commands::setText(failure_message);
            delay(5000);
            ESP.restart();
        }

        Serial.println("WiFi Ready");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        screen::commands::appendText("WiFi Connected\n");
    };

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
        .onProgress([](unsigned int progress, unsigned int total)
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

        String client_name = "flower-" + comms::flowerID();
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
            mqtt_client.subscribe("flower-control/" + comms::flowerID() + "/#");
        } else {
            String mqttFailureMessage = "\nFailed to connect to MQTT broker at\n"
                + config::CONTROLLER_IP_ADDRESS.toString();
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