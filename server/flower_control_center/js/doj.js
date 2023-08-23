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
            //subscribeToFlowerMessages();
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

function handleMQTTMessage(message) {
    if (message.destinationName.startsWith("flower-debug/")) {
        handleFlowerDebugMessage(message);
    } else if (message.destinationName.startsWith("flower-heartbeats/")) {
        handleHeartbeatMessage(message);
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


var bArray = [
    {
        'name': '1',
        'color': 'red',
        'commands': [
            '1 cmd 1',
            'wait 5',
            '1 cmd 3',
            'wait 5',
            '1 cmd 4'
        ]
    },
    {
        'name': '2',
        'color': 'green',
        'commands': [
            '2 cmd 1',
            '2 cmd 2',
            '2 cmd 3',
            '2 cmd 4'
        ]
    },
]

async function runButton(event){
    let clickedButton = event.target; // Get the clicked button element
    let buttonId = clickedButton.id; // Get the id of the clicked button

    let bObj = bArray.find(function(obj) {
        return obj.name === buttonId;
    });

    for (const cmd of bObj['commands']) {
        if(cmd.startsWith('wait')){
            let interval = parseInt(cmd.split(' ')[1])*1000
            await wait(interval)
        }else{
            console.log('running:  ', cmd)
        }
    }
}

function wait(duration) {
    return new Promise(resolve => {
        setTimeout(resolve, duration);
    });
}

function buildButtons(){
    bArray.forEach(button => {
        // Create a Bootstrap button element
        var b = document.createElement("button");
        b.textContent = button['name'];
        b.className = "btn btn-primary";
        b.id = button['name']
        b.addEventListener('click', runButton)

        // Get the target div by its ID
        var targetDiv = document.getElementById("bdiv-1");

        // Append the button to the target div
        targetDiv.appendChild(b);
    })
}


var DEBUG=true
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

    buildButtons()
});