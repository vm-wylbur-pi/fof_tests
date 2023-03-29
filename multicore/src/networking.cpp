#include "networking.h"
#include "comms.h"  // For dispatching Server commands

#include <ArduinoOTA.h>
#include <WiFi.h>
// #include <ESPmDNS.h>
// #include <WiFiUdp.h>
// #include <WiFiServer.h>
#include <MQTT.h>
#include <Arduino.h> // For String type.

namespace networking {

    // Network state objects.
    WiFiClient wifi_transport;
    MQTTClient mqtt_client;
    
    const char* WIFI_SSID = "Mariposa";
    const char* WIFI_PASSWORD = "InselKlingner2020";

    // This should be configured in the router so that it doesn't change.
    const IPAddress MQTT_BROKER_IP = IPAddress(192, 168, 1, 72);
    const char* MQTT_CLIENT_NAME = "flower";

    void setupWiFi() {
        WiFi.mode(WIFI_STA);
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        while (WiFi.waitForConnectResult() != WL_CONNECTED) {
            Serial.println("Connection Failed! Rebooting...");
            delay(5000);
            ESP.restart();
        }

        Serial.println("WiFi Ready");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
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
        })
        .onEnd([]()
        {
            Serial.println("\nEnd");
        })
        .onProgress([](unsigned int progress, unsigned int total)
        {
            Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
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
        mqtt_client.begin(MQTT_BROKER_IP, wifi_transport);
        mqtt_client.onMessage(comms::handleMessageFromControlServer);

        Serial.print("\nconnecting to MQTT broker...");
        // connect() is where we can supply username/password if we want.
        while (!mqtt_client.connect(MQTT_CLIENT_NAME))
        {
            Serial.print(".");
            delay(1000);
        }
        Serial.println("\nconnected!");

        // Main communication channel into the flower
        mqtt_client.subscribe("/flower-control/#");
    }

    bool publishMQTTMessage(const String& topic, const String& payload) {
        //Serial.println("about to publish: " + payload);
        return mqtt_client.publish(topic, payload);
    }

    void mqttSendReceive() {
        // send and receive any pending MQTT packets. If new data is received
        // this will lead to handleMQTTMessage being called
        mqtt_client.loop();
    }

}  // namespace networking;