#ifndef NETWORKING_H
#define NETWORKING_H

#include <Arduino.h>  // For String type.

namespace networking {
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

  // Should be called from the main app loop(), or a task's forever-loop
  void mqttSendReceive();

  // Publish a MQTT message to the broker.  Returns true on success.
  bool publishMQTTMessage(const String& topic, const String& payload);
}

#endif // NETWORKING_H
