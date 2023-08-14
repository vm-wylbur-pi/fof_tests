#ifndef NETWORKING_H
#define NETWORKING_H

#include <Arduino.h>  // For String type.

namespace networking {
  // Should be called from the main app setup().  Should be called before
  // any other networking:: functions.  NOTE: This will loop forever waiting
  // for one of the configured WiFi networks to be available.
  void setupWiFi();

  // Called by setupWifi to select the SSID this flower will attempt to
  // connect to.  It falls back on the SSID in config.h
  String selectSSID();

  // Should be called from the main app setup(), after setupWiFi
  void setupOTA();

  // Should be called from the main app loop(), or a task's forever-loop.
  // setupOTA must be called first.
  void checkForOTAUpdate();

  // Should be called from the main app setup(), after setupWifi
  void setupMQTT();
  void connectToMQTTBroker();
  bool isMQTTConnected();

  // Should be called from the main app loop(), or a task's forever-loop
  void mqttSendReceive();

  // Publish a MQTT message to the broker.
  void publishMQTTMessage(const String& topic, const String& payload);

  // Formatted description of WiFi signal strength
  String signalStrength();
}

#endif // NETWORKING_H
