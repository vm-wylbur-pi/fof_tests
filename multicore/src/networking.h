#ifndef NETWORKING_H
#define NETWORKING_H

#include <Arduino.h>  // For String type.

namespace networking {
  // This is used to configure:
  //   - the MQTT client
  //   - the NTP client
  // It must be running servers for both of these services. We should use the
  // router config to ensure that it always has this IP address.
  const IPAddress CONTROLLER_IP_ADDRESS = IPAddress(192, 168, 1, 72);

  // Should be called from the main app setup().  Should be called before
  // any other networking:: functions.
  void setupWiFi();

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
