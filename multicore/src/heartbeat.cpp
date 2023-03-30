#include "heartbeat.h"
#include "comms.h"
#include "networking.h"
#include "Arduino.h"

// For access to global state needed for heartbeat message.
#include <Wifi.h>
#include <FastLED.h>

void Heartbeat::BeatIfItsTime() {
    uint32_t currentMillis = millis();
    if (currentMillis - _last_heartbeat_millis > HEARTBEAT_PERIOD_MILLIS) {
        Serial.println("sending heartbeat");
        String topic = "flower-heartbeats/" + comms::flowerID();
        networking::publishMQTTMessage(topic, _makeHeartbeatMessage());
        _last_heartbeat_millis = currentMillis;
    }
}

String Heartbeat::_makeHeartbeatMessage() {
    // TODO: make this parseable (JSON or similar) so server can handle automatically
    String msg = "Flower heartbeat\n";
    msg += "  Flower ID: " + comms::flowerID() + "\n";
    msg += "  Uptime: " + _uptime.Formatted() + "\n";
    msg += "  IP: " + WiFi.localIP().toString() + "\n";
    msg += "  WiFi Signal Strength: " + networking::signalStrength() + "\n";
    msg += "  FastLED FPS: " + String(FastLED.getFPS()) + "\n";
    return msg;
}

uint32_t Uptime::Seconds() {
    return (millis() - _start_time_millis) / 1000;
}

String Uptime::Formatted() {
    uint32_t seconds = Seconds();
    if (seconds < 60) {
        return String(seconds) + " sec";
    } else if (seconds < 60*60) {
        return String(seconds/60) + " min";
    } else if (seconds < 60*60*24) {
        return String(seconds / (60*60)) + " hours " +
               String(seconds % (60*60) / 60) + " min";
    } else {
        return String(seconds / (60*60*24)) + "days " +
               String(seconds % (60*60*24) / (60*60)) + " hours";
    }
}