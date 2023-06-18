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
            subscribeToFlowerMessages();
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
            .append("<td>" + this.flower_id + "</td>")
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

    // Click handler for populating command form
    $( "#"+heartbeat.id ).children().first().click(function (event) {
        $( 'input[name="flower"]' ).val(heartbeat.flower_id);
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

function populateCommandChoices() {
    // From multicore/src/comms.cpp
    const map = new Map([
        ["foo", "Foo"],
        ["bar", "Bar"],
    ]);
    const commands = new Map([
        ["reboot",
         "Reboot this flower. No parameters."],
        // Hide this one during Patrick's party; running it with a bad or no params could break syncing.
        // ["time/setEventReference",
        // "one integer parameter, seconds since the Unix epoch. Should be in the last couple weeks."],
        ["time/setBPM",
        "one integer parameter. Affects beat-flash tempo."],
        ["leds/listPatterns",
        "Echo the sequence of currently-active LED patterns to the flower's debug stream."],
        ["leds/clearPatterns",
        "Drop all currentlny-acive LED patterns. Turns the LEDs off.  No parameters."],
        ["leds/addPattern/HuePulse",
        "A surge of color that moves up the flower. Params: hue (0-255), startTime ('+0' for right now), fadeInTime (ms), holdTime (ms), brightness (0-255)"],
        ["leds/addPattern/FairyVisit",
        "A dancing spot of yellow light.  Two params: visitDuration (ms), fairySpeed (LEDS/sec)"],
        ["leds/addPattern/IndependentIdle",
        "Shifty green leaves and a colored blossom.  No parameters."],
        ["leds/addPattern/Raindrops",
        "Random spots of light appear then fade away. Two parameters: dropsPerSecond, dropFadeTime(ms)"],
        ["leds/addPattern/SolidHue",
        "Make the whole flower (leaves+blossom) one color.  Two params: hue (0-255), startTime ('+0' for right now)"],
        ["leds/addPattern/RunningDot",
        "A white spot of light that moves up and down the flower. No parameters."],
        ["leds/addPattern/BeatFlash",
        "Flash the whole flower white briefly on each beat.  See time/setBPM.  No parameters."],
        ["audio/setVolume",
        "One float parameter between 0.0 (mute) and 11.0 (ours go to 11)"],
        ["audio/playSoundFile",
        "One string parameter, the name of sound file. See audio/listSoundFiles for choices"],
        ["audio/stopSoundFile",
        "Stops any on-going sound playback. No parameters."],
        ["audio/listSoundFiles",
        "Echo the first 30 sound files available on the flower to its debug stream."],
        ["screen/setText",
        "One string parameter (no commas). Show the given text on the tiny screen in the birdhouse."],
        ["screen/appendText",
        "One string parameter (no commas). Add the given text to whatever is currently shown on the tiny screen."],
    ]);
    commands.forEach((instructions, command) => {
        $('#command-dropDown').append(`<option value="${command}">${command}</option>`);
    });

    $('#command-dropDown').change( function() {
        let command = this.value;
        let instructions = commands.get(command);
        $('#flower_command_param_explanation').text(instructions);
    } );
}

function sendMQTTMessage(topic, payload) {
    message = new Paho.MQTT.Message(payload);
    message.destinationName = topic;
    console.log(`Sending command: ${message.destinationName}: ${message.payloadString}`);
    mqtt.publish(message);
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
        sendMQTTMessage(`flower-control/${targetFlower}/${command}`, payload)
    });

    $( "#mqtt-reconnect" ).click(function( event ) {
        connectToMQTT();  // Uses the current value of the IP address form field.
    });

    $('#flower-table').append(Heartbeat.headerRow());

    setInterval(updateFreshnessColumn, HEARTBEAT_FRESHNESS_UPDATE_PERIOD);
});