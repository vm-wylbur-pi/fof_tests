const bArray = [
    {
        'name': 'Clear Games', 'color': 'orange', 'column': 1,
        'commands': [ ['game-control/clearGames', ''] ]
    },
    {
        'name': 'Raindrops only (sparkly)', 'column': 2, 'commands': [
            ['flower-control/all/clearPatterns', ''],
            ['flower-control/all/addPattern/Raindrops', '4,3'],
        ]
    }
]

const MQTT_BROKER_PORT = 9001;
const HEARTBEAT_FRESHNESS_UPDATE_PERIOD = 1000; // milliseconds

// The singleton Pah.MQTT.Client object.
// Docs https://www.eclipse.org/paho/files/jsdoc/index.html
var mqtt;
var mqttIsConnected;  // For some reason, can't get this from the library.

function connectToMQTT() {
    $( "#mqtt-status" ).text("");
    let brokerIP = $( "#mqtt-ip" ).val();
    $( "#mqtt-status" ).append("Connecting to MQTT Broker at " + brokerIP + ":" + MQTT_BROKER_PORT + "...<br/>");
    let randomClientNameSuffix = Math.floor(Math.random() * 10000);
    mqtt = new Paho.MQTT.Client(brokerIP, Number(MQTT_BROKER_PORT),
        `DoJ_${randomClientNameSuffix}`);

    mqtt.onConnectionLost = function(context) {
        mqttIsConnected = false;
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
        onSuccess: function() {
            mqttIsConnected = true;
            $( "#mqtt-status" ).append(`Conncted to MQTT Broker at ${brokerIP}<br/>`);
            $( "#mqtt-button-nav")
                // Remove the existing class 'btn-primary'
                .removeClass("btn-danger")
                // Add the new class 'btn-danger'
                .addClass("btn-success");
            mqtt.subscribe("gsa-heartbeats");
            // request heartbeat on page load, so we get instant status in the nav bar.
            sendMQTTMessage('gsa-control/sendHeartbeat', payload='');
        },
        onFailure: function(context) {
            mqttIsConnected = false;
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

function sendMQTTMessage(topic, payload) {
    message = new Paho.MQTT.Message(payload);
    message.destinationName = topic;
    console.log(`Sending command: ${message.destinationName}: ${message.payloadString}`);
    mqtt.publish(message);
}

function handleMQTTMessage(message) {
    if (message.destinationName.startsWith("gsa-heartbeat")) {
        timeOfLastGSAHeartbeat = Date.now();
    } else {
        $( "#mqtt-status" ).append(`Received an unexpected non-heartbeat message to ${message.destinationName}<br/>`)
    }
}

function mqttConnectionMaintenance() {
    // Maybe consider some exponential backoff here.
    if (!mqttIsConnected) {
        connectToMQTT();
    }
}


async function runButton(event){
    let clickedButton = event.target; // Get the clicked button element
    let buttonId = clickedButton.id; // Get the id of the clicked button
    let nowCCOM = CCOM

    $('#' + buttonId).prop('disabled',true)
    let bObj = bArray.find(function(obj) {
        return obj.name === buttonId;
    });

    for (const cmd of bObj['commands']) {
        if(cmd.startsWith('wait')){
            let interval = parseInt(cmd.split(' ')[1])*1000
            await wait(interval)
        }else{
            if(nowCCOM != CCOM){
                console.log('breaking out because CCOM changed')
                break
            }
            console.log('running:  ', cmd)
            // This is where we actually run something
        }
    }
    $('#' + buttonId).prop('disabled',false)

}

function wait(duration) {
    return new Promise(resolve => {
        setTimeout(resolve, duration);
    });
}

function buildButtons(){
    bArray.forEach(button => {
        // Create a Bootstrap button element
        let b = document.createElement("button");
        b.textContent = button['name'];
        b.className = "btn btn-primary";
        b.id = button['name']
        b.addEventListener('click', runButton)
        if (button['color']){
            b.style.backgroundColor = button['color']
        }

        // Get the target div by its ID
        let targetDiv = document.getElementById("bdiv-" + button['column']);

        // Append the button to the target div
        targetDiv.appendChild(b);
    })
}

const GSA_HEARTBEAT_CHECK_PERIOD = 1000; // milliseconds
const GSA_SILENCE_TO_WORRY_ABOUT = 10000;  // milliseconds
var timeOfLastGSAHeartbeat = 0;
function checkGSAHeartbeatAge() {
    let millisSinceLastHeartbeat = Date.now() - timeOfLastGSAHeartbeat;
    if (millisSinceLastHeartbeat > GSA_SILENCE_TO_WORRY_ABOUT) {
        $( "#gsa-button-nav").removeClass("btn-success").addClass("btn-danger");
    } else {
        $( "#gsa-button-nav").removeClass("btn-danger").addClass("btn-success");
    }
}

var DEBUG=true
var CCOM = Math.random()
$( document ).ready(function() {

    var currentUrl = window.location.href;

    // Check if the "debug" query string parameter is present
    if (! currentUrl.includes("debug")) {
        $('#mqttROW').hide()
        $('#mqttReconnectRow').hide()
        DEBUG=false
    }

    connectToMQTT();
    setInterval(mqttConnectionMaintenance, 1000);  // milliseconds
    $( "#mqtt-reconnect" ).click(function( event ) {
        connectToMQTT();  // Uses the current value of the IP address form field.
    });

    $("#ClearButtons").click(event => {
        CCOM = Math.random()
        var allButtons = $("button");

        // Loop through each button and enable it
        allButtons.each(function() {
            $(this).prop("disabled", false);
        });
    })

    setInterval(checkGSAHeartbeatAge, GSA_HEARTBEAT_CHECK_PERIOD);

    buildButtons()
});