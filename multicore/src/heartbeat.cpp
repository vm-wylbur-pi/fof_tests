#include "heartbeat.h"

#include "audio.h"
#include "flower_info.h"
#include "networking.h"
#include "storage.h"
#include "time_sync.h"
#include "version.h"

#include <Arduino.h>

// For access to global state needed for heartbeat message.
#include <FastLED.h>
#include <WiFi.h>

void Heartbeat::BeatIfItsTime() {
    uint32_t currentMillis = millis();
    if (currentMillis - _last_heartbeat_millis > HEARTBEAT_PERIOD_MILLIS) {
        Beat();
        _last_heartbeat_millis = currentMillis;
    }
}

void Heartbeat::Beat() {
    Serial.println("sending heartbeat");
    String topic = "flower-heartbeats/" + flower_info::flowerID();
    networking::publishMQTTMessage(topic, _makeHeartbeatMessage());
}

String Heartbeat::_makeHeartbeatMessage() {
    // Makes a JSON heartbeat message that will be interpreted by the flower control center
    // See flower_control_center/main.js:Heartbeat.toRow for the expected field names
    String msg = "{";
    msg += "  \"flower_id\": \"" + flower_info::flowerID() + "\",\n";
    msg += "  \"sequence_num\": \"" + String(flower_info::flowerInfo().sequenceNum) + "\",\n";
    msg += "  \"uptime\": \"" + _uptime.Formatted() + "\",\n";
    msg += "  \"version_name\": \"" + version::Name + "\",\n";
    msg += "  \"build_timestamp\": \"" + version::getBuildTime() + "\",\n";
    msg += "  \"IP\": \"" + WiFi.localIP().toString() + "\",\n";
    msg += "  \"SSID\": \"" + WiFi.SSID() + "\",\n";
    msg += "  \"wifi_signal\": \"" + networking::signalStrength() + "\",\n";
    msg += "  \"sd_card\": \"" + storage::formatStorageUsage() + "\",\n";
    msg += "  \"volume\": \"" + audio::formattedVolume() + "\",\n";
    msg += "  \"ntp_time\": \"" + time_sync::getFormattedNTPTime() + "\",\n";
    msg += "  \"control_timer\": \"" + String(time_sync::controlMillis()) + " ms\",\n";
    msg += "  \"FastLED_fps\": \"" + String(FastLED.getFPS()) + "\"\n";
    msg += "}";
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