const bArray = [
    {
        'name': 'Clear Games', 'color': 'darkorange', 'column': 1,
        'resets_buttons': true,
        'commands': [ ['game-control/clearGames', ''] ]
    },
    {
        'name': 'Clear Games & Reset Flowers', 'color': 'darkorange', 'column': 1,
        'resets_buttons': true,
        'commands': [ ['game-control/resetField', ''] ]
    },
    {
        'name': 'All LEDs off with power-down sound', 'color': 'darkorange', 'column': 1,
        'resets_buttons': true,
        'commands': [ ['flower-control/all/leds/clearPatterns', ''],
                      ['flower-control/all/audio/playSoundFile', 'punctuation/PunctuationDOWN.wav'] ]
    },
    {
        'name': '→ Straight Wave, left-to-right', 'color': 'teal', 'column': 1,
        'commands': [ ['game-control/runGame/StraightColorWave', '160,0,450,550,0,+500'] ]
    },
    {
        'name': '← Straight Wave, right-to-left', 'color': 'teal', 'column': 1,
        'commands': [ ['game-control/runGame/StraightColorWave', '110,1000,450,-600,0,+500'] ]
    },
    {
        'name': '↑ Straight Wave, bottom-to-top', 'color': 'teal', 'column': 1,
        'commands': [ ['game-control/runGame/StraightColorWave', '200,550,1000,0,-600,+500'] ]
    },
    {
        'name': '↓ Straight Wave, top-to-bottom', 'color': 'teal', 'column': 1,
        'commands': [ ['game-control/runGame/StraightColorWave', '40,350,0,0,600,+500'] ]
    },
    {
        'name': '⊕ Expanding Circle from center', 'color': 'teal', 'column': 1,
        'commands': [ ['game-control/runGame/CircularColorWave', '180,500,500,0,600,+500'] ]
    },
    {
        'name': '⊖ Contracting Circle to center', 'color': 'teal', 'column': 1,
        'commands': [ ['game-control/runGame/CircularColorWave', '20,500,500,550,-600,+500'] ]
    },
    {
        'name': 'Random Waves, indefinitely', 'color': 'navy', 'column': 1,
        'commands': [ ['game-control/runGame/RandomWaves', '20,500,500,550,-600,+500'] ]
    },
    {
        'name': 'Running Light', 'color': 'darkgreen', 'column': 1,
        'commands': [ ['game-control/runGame/RunningLight', '+0,15,100'] ]
    },

    {
        'name': 'Field Idle - cycle through several games', 'color': 'grey', 'column': 2,
        'commands': [ ['game-control/runGame/FieldIdle', ''] ]
    },
    {
        'name': 'Add Fairy', 'color': 'darkgoldenrod', 'column': 2,
        'commands': [ ['game-control/runGame/Fairy', ''] ]
    },
    {
        'name': 'Roll Call', 'color': 'darkgoldenrod', 'column': 2,
        'commands': [ ['game-control/runGame/RollCall', '500'] ]
    },
    {
        'name': 'Sound Waves - targets people', 'color': 'darkgoldenrod', 'column': 2,
        'commands': [ ['game-control/runGame/Wave', ''] ]
    },
    {
        'name': 'Bouncing Blob', 'color': 'darkgoldenrod', 'column': 2,
        'commands': [ ['game-control/runGame/BouncingBlob', '400,150'] ]
    },

    {
        'name': 'Gossip', 'color': 'darkmagenta', 'column': 2,
        'commands': [ ['game-control/runGame/Gossip', ''] ]
    },
    {
        'name': 'Big Ben chimes 4 o-clock', 'color': 'darkmagenta', 'column': 2,
        'commands': [
            // Since we don't have a separate just-2nd-part sound file, play all at once
            ['gsa-control/playSoundNearPoint', 'bigben/quarter.wav,500,0'],
            ['gsa-control/playSoundNearPoint', 'bigben/halfhour.wav,950,50'],
            ['gsa-control/playSoundNearPoint', 'bigben/threequarter.wav,500,900'],
            ['gsa-control/playSoundNearPoint', 'bigben/preamble.wav,20,500'],
            ['wait', 15000],
            ['flower-control/all/audio/playSoundFile', 'bigben/4dongs.wav'],
        ]
    },
    {
        'name': 'All flowers dong once', 'color': 'darkmagenta', 'column': 2,
        'commands': [ ['flower-control/all/audio/playSoundFile', 'bigben/1dong.wav'] ]
    },
    {
        'name': 'Play overture on 10 flowers', 'color': 'darkmagenta', 'column': 2,
        'commands': [
            ['flower-control/10/audio/playSoundFile', 'long-songs/FieldofFlowersOverture.wav'],
            ['flower-control/30/audio/playSoundFile', 'long-songs/FieldofFlowersOverture.wav'],
            ['flower-control/50/audio/playSoundFile', 'long-songs/FieldofFlowersOverture.wav'],
            ['flower-control/70/audio/playSoundFile', 'long-songs/FieldofFlowersOverture.wav'],
            ['flower-control/90/audio/playSoundFile', 'long-songs/FieldofFlowersOverture.wav'],
            ['flower-control/110/audio/playSoundFile', 'long-songs/FieldofFlowersOverture.wav'],
            ['flower-control/130/audio/playSoundFile', 'long-songs/FieldofFlowersOverture.wav'],
            ['flower-control/150/audio/playSoundFile', 'long-songs/FieldofFlowersOverture.wav'],
        ]
    },
    {
        'name': 'Chorus Circle', 'color': 'darkmagenta', 'column': 2,
        'commands': [ ['game-control/runGame/ChorusCircle', '30,5.0'] ]
    },


    {
        'name': 'Raindrops only', 'column': 2, 
        'resets_buttons': true,
        'commands': [
            ['flower-control/all/clearPatterns', ''],
            ['flower-control/all/addPattern/Raindrops', '4,3'],
        ]
    },
    {
        'name': 'two waves with a pause', 'column': 2,
        'commands': [
            ['game-control/runGame/CircularColorWave', ''],
            ['wait', 3000],
            ['game-control/runGame/CircularColorWave', ''],
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
        handleGSAHeartbeat(message);
    } else {
        $( "#mqtt-status" ).append(`Received an unexpected non-heartbeat message to ${message.destinationName}<br/>`)
    }
}

function handleGSAHeartbeat(message) {
    timeOfLastGSAHeartbeat = Date.now();
    try {
        const data = JSON.parse(message.payloadString);
        let gsaStatusMsg = `The camera sees ${data['num_people']} people. `
        if (data['games'].length == 0) {
            gsaStatusMsg += `Active games: none`
        } else {
            gsaStatusMsg += `Active games: ${data['games'].join(', ')}`
        }
        $("#gsaStatus").html(gsaStatusMsg);
    } catch(e) {
        console.log(`Error handling heartbeat message from the GSA`);
        console.log(e);
        console.log(message.payloadString);
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

    console.log(`disabling button ${buttonId}`)
    $('#' + buttonId).prop('disabled',true)
    let bObj = bArray.find(function(obj) {
        return obj.name === buttonId;
    });

    for (const cmd of bObj['commands']) {
        if (bObj['ressets_buttons']) {
            resetButtons();  // resets CCOM, ending all waits.
        }
        if (cmd.length != 2) {
            console.log(`command array has ${cmd.length} elements instead of 2`);
            return;
        }
        if(cmd[0] == 'wait') {
            let interval = cmd[1]; // milliseconds
            await wait(interval)
        }else{
            if(nowCCOM != CCOM){
                console.log('breaking out because CCOM changed')
                break
            }
            console.log('running:  ', cmd)
            let topic = cmd[0];
            let payload = cmd[1];
            sendMQTTMessage(topic, payload);
        }
    }
    console.log(`enabling button ${buttonId}`)
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

function resetButtons() {
    console.log("running resetButtons")
    CCOM = Math.random();  // causes all waits to be abandoned
    var allButtons = $("button");

    // Loop through each button and enable it
    allButtons.each(function() {
        $(this).prop("disabled", false);
    });
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

    $("#ResetButtons").click(event => {
        resetButtons();
    })

    setInterval(checkGSAHeartbeatAge, GSA_HEARTBEAT_CHECK_PERIOD);

    buildButtons()
});