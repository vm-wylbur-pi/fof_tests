#ifndef COMMS_H
#define COMMS_H

#include <Arduino.h>  // For String type

// Functions related to communication to/from the control server.
// All communication uses MQTT
//
// Lower-level communication (wifi, OTA, and MQTT setup) are in networking.h
// All comms in this file run on top of MQTT.
namespace comms
{
  // Publish a general-purpose debug message.  We can set up various ways
  // to monitor these.
  void sendDebugMessage(String& msg);

  // Publish a heartbeat message.  This will include flower identification
  // info and status.
  void sendHeartbeat();

  void setupComms();

  void mainLoop();

  // This is central dispatch function for all communication and commands
  // received from the control server. It is registered as the main MQTT
  // callback in networking::setupMQTT.
  void handleMessageFromControlServer(String& topic, String& payload);
}  // namespace comms

#endif // COMMS_H