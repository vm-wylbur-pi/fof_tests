const MQTT_BROKER_PORT = 9001;

const HEARTBEAT_FRESHNESS_UPDATE_PERIOD = 1000; // milliseconds

// The singleton Pah.MQTT.Client object.
// Docs https://www.eclipse.org/paho/files/jsdoc/index.html
var mqtt;

function connectToMQTT() {
    $( "#mqtt-status" ).text("");
    let brokerIP = $( "#mqtt-ip" ).val();
    $( "#mqtt-status" ).append("Connecting to MQTT Broker at " + brokerIP + ":" + MQTT_BROKER_PORT + "...<br/>");
    mqtt = new Paho.MQTT.Client(brokerIP, MQTT_BROKER_PORT, "Flower_Control_Center");

    mqtt.onConnectionLost = function(context) {
        $( "#mqtt-status" ).append(`MQTT connection lost: ${context.errorMessage}<br/>`);
    };
    mqtt.onMessageArrived = handleMQTTMessage;

    var connect_options = {
        timeout: 5,  // seconds
        onSuccess: function() {
            $( "#mqtt-status" ).append("Conncted to MQTT Broker.<br/>");
            subscribeToHeartbeats();
        },
        onFailure: function(context) {
            $( "#mqtt-status" ).append(`MQTT connection failed: ${context.errorMessage}<br/>`);
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
            .append("<th>Heartbeat age</th>")
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
            .append('<td heartbeat_timestamp="' + this.creation_timestamp + '">:00</td>')
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

function subscribeToHeartbeats() {
    mqtt.subscribe("flower-heartbeats/#", {
        onSuccess: function() {
            $( "#mqtt-status" ).append("Subscribed to flower-heartbeats/#<br/>")
        },
        onFailure: function(response) {
            $( "#mqtt-status" ).append(response.errorMessage);
        }
    });
}

function handleMQTTMessage(message) {
    if (!message.destinationName.startsWith("flower-heartbeats/")) {
        $( "#mqtt-status" ).append(`Received an unexpected non-heartbeat message to ${message.destinationName}<br/>`)
    }
    insertOrUpdateFlowerRow(new Heartbeat(message.payloadString));
}

function insertOrUpdateFlowerRow(heartbeat) {
    let row = $("#flower-table").find("#" + heartbeat.id);
    if (row.length == 0) {
        console.log("Adding new flower: " + heartbeat.flower_id);
        $("#flower-table").append(heartbeat.toRow());
    } else {
        console.log("updating flower " + heartbeat.flower_id);
        row.replaceWith(heartbeat.toRow());
    }

    // Green Heartbeat pulse effect
    $( "#"+heartbeat.id )
        .css( { backgroundColor: "#0f0" } )
        .animate( { backgroundColor: "#eee" }, 500 );

    // Click handler for populating command form
    $( "#"+heartbeat.id ).children().first().click(function (event) {
        $( 'input[name="flower"]' ).val(heartbeat.flower_id);
    })
}

function formatHeartbeatAge(age_milliseconds) {
    // Convert to a readable timer, using a Date object to represent time since the epoch
    let age_timer = new Date();
    age_timer.setTime(age_milliseconds);
    if (age_timer.getUTCHours > 0) {
        return "> 1 hour";
    }
    let minutes = age_timer.getUTCMinutes().toString().padStart(2, "0");
    let seconds = age_timer.getUTCSeconds().toString().padStart(2, "0");
    if (minutes == "00") {
        minutes = ""; 
    }
    return `${minutes}:${seconds}`
}

function updateFreshnessColumn() {
    current_timestamp = Date.now();
    $('#flower-table td[heartbeat_timestamp]').each(function(i, elem) {
        // age is milliseconds since the heartbeat was created
        let age_millis = current_timestamp - $( this ).attr("heartbeat_timestamp");
        $( this ).text(formatHeartbeatAge(age_millis));
    });
}

function populateCommandChoices() {
    // From multicore/src/comms.cpp
    const commands = [
        "reboot",
        "time/setEventReference",
        "time/setBPM",
        "leds/toggleBeatFlashing",
        "leds/setHue",
        "audio/setVolume",
        "audio/playSoundFile",
        "audio/stopSoundFile"
    ]
    commands.forEach((command) => {
        $('#command-dropDown').append(`<option value="${command}">${command}</option>`)
    })
}

$( document ).ready(function() {
    connectToMQTT();

    populateCommandChoices();
    
    $( "span#all" ).on("click", function( event ) {
        $( 'input[name="flower"]' ).val("all");
    });

    $( "#send-command" ).click(function( event ) {
        let targetFlower = $('input[name="flower"]').val();
        let command = $('select[name="command"]').val();
        let payload = $('input[name="parameters"]').val();
        message = new Paho.MQTT.Message(payload);
        message.destinationName = `flower-control/${targetFlower}/${command}`;
        console.log(`Sending command: ${message.destinationName}: ${message.payloadString}`);
        mqtt.publish(message);
    });

    $( "#mqtt-reconnect" ).click(function( event ) {
        connectToMQTT();  // Uses the current value of the IP address form field.
    });

    $('#flower-table').append(Heartbeat.headerRow());

    setInterval(updateFreshnessColumn, HEARTBEAT_FRESHNESS_UPDATE_PERIOD);
});