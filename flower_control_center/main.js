const MQTT_BROKER_IP = "192.168.1.72";
const MQTT_BROKER_PORT = 9001;

const HEARTBEAT_FRESHNESS_UPDATE_PERIOD = 1000; // milliseconds

// The singlenot Pah.MQTT.Client object.
var mqtt;

function connectToMQTT() {
    console.log("Connecting to MQTT Broker at " + MQTT_BROKER_IP + ":" + MQTT_BROKER_PORT);
    mqtt = new Paho.MQTT.Client(MQTT_BROKER_IP, MQTT_BROKER_PORT, "Flower_Control_Center");
    var connect_options = {
        timeout: 2000,
        onSuccess: function() {
            document.write("Conncted to MQTT Broker.")
        }
    }
    mqtt.connect(connect_options);
}

class Heartbeat {
    constructor(heartbeat_json) {
        const data = JSON.parse(heartbeat_json);
        for (var field in data) {
            this[field] = data[field];
        }
        // Id for HTML can't have colons.  42:A1:94 -> 42_A1_94
        this.id = this.flower_id.replaceAll(":","_");
        this.creation_timestamp = Date.now();
    }

    static headerRow() {
        return $("<tr>")
            .append("<th>Flower ID</th>")
            .append("<th>Heartbeat age<th>")
            .append("<th>Uptime</th>")
            .append("<th>IP</th>")
            .append("<th>WiFi Signal Strength</th>")
            .append("<th>SD Card</th>")
            .append("<th>Audio Volume</th>")
            .append("<th>Time from NTP</th>")
            .append("<th>control Timer</th>")
            .append("<th>FastLED FPS</th>")
    }

    toRow () {
        return $("<tr>")
            .append("<td>" + this.flower_id + "</td>")
            .append('<td heartbeat_timestamp="' + this.creation_timestamp + '">0</td>')
            .append("<td>" + this.uptime + "</td>")
            .append("<td>" + this.IP + "</td>")
            .append("<td>" + this.wifi_signal + "</td>")
            .append("<td>" + this.sd_card + "</td>")
            .append("<td>" + this.volume + "</td>")
            .append("<td>" + this.ntp_time + "</td>")
            .append("<td>" + this.control_timer + "</td>")
            .append("<td>" + this.FastLED_fps + "</td>")
            .attr("id", this.id);
    }
};

const flower_1_json = `
{
  "flower_id": "42:11:94",
  "uptime": "2 hours 29 min",
  "IP": "192.168.1.203",
  "wifi_signal": "-46 dBm (Excellent)",
  "sd_card": "37/14855 MB",
  "volume": "10/21",
  "ntp_time": "15:38:44.884",
  "control_timer": "141067888",
  "FastLED_fps": "325"
}
`;

const flower_2_json = `
{
  "flower_id": "A2:A1:94",
  "uptime": "2 hours 29 min",
  "IP": "192.168.1.203",
  "wifi_signal": "-46 dBm (Excellent)",
  "sd_card": "37/14855 MB",
  "volume": "10/21",
  "ntp_time": "15:38:44.884",
  "control_timer": "141067888",
  "FastLED_fps": "325"
}
`;

function insertOrUpdateFlowerRow(heartbeat) {
    let row = $("#flower-table").find("#" + heartbeat.id);
    if (row.length == 0) {
        console.log("Adding new flower");
        $("#flower-table").append(heartbeat.toRow());
    } else {
        console.log("updating flower");
        row.replaceWith(heartbeat.toRow());
    }
}

function updateFreshnessColumn() {
    current_timestamp = Date.now();
    $('#flower-table td[heartbeat_timestamp]').each(function(i, elem) {
        // age is milliseconds since the heartbeat was created
        let age = current_timestamp - $( this ).attr("heartbeat_timestamp");
        // Convert to a readable timer, using a Date object to represent time since the epoch
        let age_timer = new Date();
        age_timer.setTime(age);
        let minutes = age_timer.getUTCMinutes().toString().padStart(2, "0");
        let seconds = age_timer.getUTCSeconds().toString().padStart(2, "0");
        if (minutes == "00") {
            minutes = ""; 
        }
        $( this ).text(`${minutes}:${seconds}`);

    });
}

$( document ).ready(function() {
    //connectToMQTT();
    
    $('#flower-table').append(Heartbeat.headerRow());
    
    let heartbeat = new Heartbeat(flower_1_json);
    insertOrUpdateFlowerRow(heartbeat);
    heartbeat = new Heartbeat(flower_2_json)
    insertOrUpdateFlowerRow(heartbeat);

    setInterval(updateFreshnessColumn, HEARTBEAT_FRESHNESS_UPDATE_PERIOD);
});