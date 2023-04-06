#include "networking.h"
#include "comms.h"  // For dispatching Server commands

#include <Arduino.h> // For String type.
#include <ArduinoOTA.h>
#include <WiFi.h>
// #include <ESPmDNS.h>
// #include <WiFiUdp.h>
// #include <WiFiServer.h>
#include <MQTT.h>

namespace networking {

    const char *WIFI_SSID = "Mariposa";
    const char *WIFI_PASSWORD = "InselKlingner2020";

    // Will set the buffer size for sending and receiving.  Messages
    // exceeding this limit will fail to send.
    const uint16_t MAX_MQTT_MESSAGE_BYTES = 512;

    // Network state objects.
    WiFiClient wifi_client;
    MQTTClient mqtt_client(MAX_MQTT_MESSAGE_BYTES);

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
        mqtt_client.begin(CONTROLLER_IP_ADDRESS, wifi_client);
        mqtt_client.onMessage(comms::handleMessageFromControlServer);
        connectToMQTTBroker();
    }

    void connectToMQTTBroker() {
        Serial.print("\nconnecting to MQTT broker...");
        String client_name = "flower-" + comms::flowerID();
        // connect() is where we can supply username/password if we want.
        while (!mqtt_client.connect(client_name.c_str())) {
            Serial.print(".");
            delay(1000);
        }
        Serial.println("\nconnected!");

        // Main communication channel into the flower
        // Control commands directed at all flowers.
        mqtt_client.subscribe("flower-control/all/#");
        // Control commands directed at just this flower.
        mqtt_client.subscribe("flower-control/" + comms::flowerID() + "/#");
    }

    bool isMQTTConnected() {
        return mqtt_client.connected();
    }

    void publishMQTTMessage(const String& topic, const String& payload) {
        bool success = mqtt_client.publish(topic, payload);
        if (!success) {
            Serial.println("Failed to publish MQTT message in " + topic);
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