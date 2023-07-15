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
  // To be called from a top-level task forever-loop.  Handles MQTT
  // connection maintenance, send/receive flushes of queued MQTT 
  // messages, and heartbeats.
  void mainLoop();

  // Send a heartbeat outside the normal heartbeat timer loop. Used 
  // to send a single beat during wake-then-back-to-sleep cycle.
  void forceHeartbeat();

  // Publish a general-purpose debug message.  We can set up various ways
  // to monitor these.  To avoid deadlock, this only sends messages at QoS == 0.
  // (To avoid deadlock, publish() should generally not be called from a message
  // handler. See  https://registry.platformio.org/libraries/256dpi/MQTT
  void sendDebugMessage(const String& msg);

  // This is central dispatch function for all communication and commands
  // received from the control server. It is registered as the main MQTT
  // callback in networking::setupMQTT.
  void handleMessageFromControlServer(String& topic, String& payload);

  // Called by handleMessageFromControlServer to dispatch flower control commands.
  void dispatchFlowerControlCommand(String &command, String &parameters);
}  // namespace comms

#endif // COMMS_H