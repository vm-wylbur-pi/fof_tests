const MQTT_BROKER_PORT = 9001;

const HEARTBEAT_FRESHNESS_UPDATE_PERIOD = 1000; // milliseconds

// The singleton Pah.MQTT.Client object.
// Docs https://www.eclipse.org/paho/files/jsdoc/index.html
var mqtt;

function connectToMQTT() {
    $( "#mqtt-status" ).text("");
    let brokerIP = $( "#mqtt-ip" ).val();
    $( "#mqtt-status" ).append("Connecting to MQTT Broker at " + brokerIP + ":" + MQTT_BROKER_PORT + "...<br/>");
    let randomClientNameSuffix = Math.floor(Math.random() * 10000);
    mqtt = new Paho.MQTT.Client(brokerIP, MQTT_BROKER_PORT,
                                `Flower_Control_Center_${randomClientNameSuffix}`);

    mqtt.onConnectionLost = function(context) {
        $( "#mqtt-status" ).append(`MQTT connection lost: ${context.errorMessage}<br/>`);
        $( "#mqtt-button-nav")
            // Remove the existing class 'btn-primary'
            .removeClass("btn-success")
            // Add the new class 'btn-danger'
            .addClass("btn-danger");
    };
    mqtt.onMessageArrived = handleMQTTMessage;

    var connect_options = {
        timeout: 5,  // seconds
        reconnect: true,  // exponential backoff maxing at 2-minute retry loop
        onSuccess: function(reconnected) {
            let msg = `Conncted to MQTT Broker at ${brokerIP}<br/>`
            if (reconnected) {
                msg = "Re-" + msg;
            }
            $( "#mqtt-status" ).append(msg);
            $( "#mqtt-button-nav")
                // Remove the existing class 'btn-primary'
                .removeClass("btn-danger")
                // Add the new class 'btn-danger'
                .addClass("btn-success");
            subscribeToFlowerMessages();
        },
        onFailure: function(context) {
            $( "#mqtt-status" ).append(`MQTT connection failed: ${context.errorMessage}<br/>`);
            $( "#mqtt-button-nav")
                // Remove the existing class 'btn-primary'
                .removeClass("btn-success")
                // Add the new class 'btn-danger'
                .addClass("btn-danger");
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
            .append("<th>Flower Num</th>")
            .append("<th>Debug Messages</th>")
            .append("<th>Heartbeat age</th>")
            .append("<th>Uptime</th>")
            .append("<th>Firmware Version</th>")
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
            .append('<td class="flower_id">' + this.flower_id + "</td>")
            .append('<td class="flower_num">' + this.sequence_num + "</td>")
            .append("<td><button>show</button></td>")
            .append('<td heartbeat_timestamp="' + this.creation_timestamp + '">:00</td>')
            .append("<td>" + this.uptime + "</td>")
            .append("<td>" + this.version_name + " (built " + this.build_timestamp + ")</td>")
            .append("<td class='ip'>" + this.IP + "</td>")
            .append("<td>" + this.wifi_signal + "</td>")
            .append("<td>" + this.sd_card + "</td>")
            .append("<td>" + this.volume + "</td>")
            .append("<td>" + this.ntp_time + "</td>")
            .append("<td>" + this.control_timer + "</td>")
            .append("<td>" + this.FastLED_fps + "</td>")
            .attr("id", this.id);
    }
};

function subscribeToFlowerMessages() {
    const topics = ["flower-heartbeats/#", "flower-debug/#"];
    topics.forEach(function(topic) {
        mqtt.subscribe(topic, {
            onSuccess: function() {
                $( "#mqtt-status" ).append(`Subscribed to ${topic}<br/>`)
            },
            onFailure: function(response) {
                $( "#mqtt-status" ).append(response.errorMessage);
            }
        });
    });
}

function handleMQTTMessage(message) {
    if (message.destinationName.startsWith("flower-debug/")) {
        handleFlowerDebugMessage(message);
    } else if (message.destinationName.startsWith("flower-heartbeats/")) {
        handleHeartbeatMessage(message);
    } else {
        $( "#mqtt-status" ).append(`Received an unexpected non-heartbeat message to ${message.destinationName}<br/>`)
    }
}

function handleFlowerDebugMessage(message) {
    const prefixLen = "flower-debug/".length;
    let flower_id = message.destinationName.substring(prefixLen);
    console.log(`got debug message from flower ${flower_id}`);
    let $debugDiv = findOrCreateDebugDiv(flower_id);
    $debugDiv.append(`<pre>${message.payloadString}</pre>`)
}

function findOrCreateDebugDiv(flower_id) {
    let debugDivID = "debug_" + flower_id.replaceAll(":","_");
    var $debugDiv = $( '#'+debugDivID );
    if(!$debugDiv.length) {
        // No debug messages from this flower yet, create a new div for them.
        $debugDiv = $(`<div id="${debugDivID}"></div>`).appendTo('#debugContainer');
        $debugDiv.addClass("debugMessages");
        $debugDiv.append(
            `<h3>
                <button class="close">close</button>
                Debug messages for flower ${flower_id.replaceAll("_",":")}
                <button class="clear">clear</button>
             </h3>`);
        $debugDiv.hide()

        $debugDiv.find(".close").click(function(event) {
            $debugDiv.hide();
        });
        $debugDiv.find(".clear").click(function(event) {
            $debugDiv.find("pre").remove();
        });
    }
    return $debugDiv;
}

function handleHeartbeatMessage(message) {
    try {
        let heartbeat = new Heartbeat(message.payloadString);
        insertOrUpdateFlowerRow(heartbeat);
    } catch(e) {
        console.log(`Error handling heartbeat message from ${message.destinationName}`);
        console.log(e);
        console.log(message.payloadString);
    }
}

function insertOrUpdateFlowerRow(heartbeat) {
    let row = $("#flower-table").find("#" + heartbeat.id);
    if (row.length == 0) {
        //console.log("Adding new flower: " + heartbeat.flower_id);
        $("#flower-table").append(heartbeat.toRow());

        // Account for this new flower in the Mass OTA command tool
        updateMassOTACommand();
    } else {
        //console.log("updating flower " + heartbeat.flower_id);
        row.replaceWith(heartbeat.toRow());
    }

    // Green Heartbeat pulse effect
    $( "#"+heartbeat.id )
        .css( { backgroundColor: "#0f0" } )
        .animate( { backgroundColor: "#eee" }, 500 );

    // Click handler for populating command form with flower number or ID
    $( "#"+heartbeat.id ).children(".flower_id").click(function (event) {
        $( 'input[name="flower"]' ).val(heartbeat.flower_id);
    });
    $( "#"+heartbeat.id ).children(".flower_num").click(function (event) {
        $( 'input[name="flower"]' ).val(heartbeat.sequence_num);
    });

    // Click handler for showing debug messages from this flower.
    $( "#"+heartbeat.id+" button").click(function (event) {
        let $debugDiv = findOrCreateDebugDiv(heartbeat.id);
        $debugDiv.show();
    });
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

function sendMQTTMessage(topic, payload) {
    message = new Paho.MQTT.Message(payload);
    message.destinationName = topic;
    console.log(`Sending command: ${message.destinationName}: ${message.payloadString}`);
    mqtt.publish(message);
}

$( document ).ready(function() {
    connectToMQTT();

    $( "#mqtt-reconnect" ).click(function( event ) {
        connectToMQTT();  // Uses the current value of the IP address form field.
    });

    $('#flower-table').append(Heartbeat.headerRow());

    setInterval(updateFreshnessColumn, HEARTBEAT_FRESHNESS_UPDATE_PERIOD);
});