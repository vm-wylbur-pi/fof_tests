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
        'name': 'Sound Waves - targets people', 'color': 'navy', 'column': 1,
        'commands': [ ['game-control/runGame/Wave', ''] ]
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
        'name': 'Start a Fairy mob', 'color': 'darkgoldenrod', 'column': 2,
        'commands': [ ['game-control/runGame/FairyMob', ''] ]
    },
    {
        'name': 'Roll Call', 'color': 'darkgoldenrod', 'column': 2,
        'commands': [ ['game-control/runGame/RollCall', '500'] ]
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
            // Prelude chimes just on 8 flowers
            ['game-control/runGame/PlaySoundOnMultipleFlowers', 'bigben/preamble.wav,8'],
            // Time for the prelude to play
            ['wait', 15000],
            // Dongs on half of the flowers
            ['game-control/runGame/PlaySoundOnMultipleFlowers', 'bigben/4dongs.wav,80'],
        ]
    },
    {
        'name': 'Long track: Overture (7 min)', 'color': 'darkmagenta', 'column': 2,
        'commands': [
            ['game-control/runGame/PlaySoundOnMultipleFlowers',
             'long-songs/FieldofFlowersOverture.wav,10'],
        ]
    },
    {
        'name': 'Long track: Flower Party (4 min)', 'color': 'darkmagenta', 'column': 2,
        'commands': [
            ['game-control/runGame/PlaySoundOnMultipleFlowers',
             'long-songs/CulminatingFlowerParty_wavegame2.wav,10'],
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
    buildBrightnessSliderRow();
    buildVolumeSliderRow();

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

    buildHueKeyedButtons(document.getElementById("bdiv-1-hue-pulse"),
                         headerText="Hue Pulse",
                         topic="gsa-control/relayToAllFlowersWithThrottling/leds/addPattern/HuePulse",
                         makePayload = function(hue) { return `${hue},+0` })
    
    buildHueKeyedButtons(document.getElementById("bdiv-1-whole-flower"),
                         headerText="Whole Flower",
                         topic="gsa-control/relayToAllFlowersWithThrottling/leds/addPattern/SolidHue",
                         makePayload = function(hue) { return `${hue},+0` })

    buildHueKeyedButtons(document.getElementById("bdiv-1-blossom-only"),
                         headerText="Blossom Only",
                         topic="gsa-control/relayToAllFlowersWithThrottling/leds/addPattern/BlossomColor",
                         makePayload = function(hue) { return `${hue},250,200,255,+0` })

    buildSoundButtons();
}

function buildSoundButtons() {
    let sounds = [
        ["dong", ["bigben/1dong.wav"]],
        ["flutter", ["punctuation/PunctuationFlutter.wav"]],
        ["zip-up", ["punctuation/PunctuationUP.wav"]],
        ["zip-down", ["punctuation/PunctuationDOWN.wav"]],
        ["zip-updown", ["punctuation/PunctuationUPDOWN.wav"]],
        ["giggle", ["fairy/MikaylaGiggle1.wav",
                    "fairy/MikaylaGiggle2.wav",
                    "fairy/MikaylaGiggle3.wav",
                    "fairy/MikaylaGiggle4.wav",
                    "fairy/MikaylaGiggle5.wav",
                    "fairy/MikaylaGiggle6.wav",
                    "fairy/MikaylaGiggle7.wav"]],
        ["ha", ["wave/ha1.wav","wave/ha2.wav","wave/ha3.wav",
                "wave/ha4.wav","wave/ha5.wav","wave/ha6.wav"]],
        ["hi", ["wave/Hi1.wav","wave/Hi2.wav","wave/Hi3.wav",
                "wave/Hi4.wav","wave/Hi5.wav","wave/Hi6.wav"]],
        ["he", ["wave/He1.wav","wave/He2.wav","wave/He3.wav",
                "wave/He4.wav",              ,"wave/He6.wav"]],
        ["mm", ["wave/mm1.wav","wave/mm2.wav","wave/mm3.wav",
                "wave/mm4.wav","wave/mm5.wav","wave/mm6.wav"]],
        ["oa", ["wave/oa1.wav","wave/oa2.wav","wave/oa3.wav",
                "wave/oa4.wav","wave/oa5.wav","wave/oa6.wav"]],
        ["oh", ["wave/OO1.wav","wave/OO2.wav","wave/OO3.wav",
                "wave/OO4.wav","wave/OO5.wav","wave/OO6.wav"]],
        ["oo-oo", ["wave/oo-oo1.wav","wave/oo-oo2.wav","wave/oo-oo3.wav",
                   "wave/oo-oo4.wav","wave/oo-oo5.wav","wave/oo-oo6.wav"]],
        ["yeah", ["wave/yeah1.wav","wave/yeah2.wav","wave/yeah3.wav",
                  "wave/yeah4.wav","wave/yeah5.wav","wave/yeah6.wav"]],
        ["yeahUP", ["wave/yeahUP1.wav","wave/yeahUP2.wav","wave/yeahUP3.wav",
                    "wave/yeahUP4.wav","wave/yeahUP5.wav","wave/yeahUP6.wav"]],
        ["night", ["punctuation/goodnight1_jill.wav","punctuation/goodnight2_jill.wav",
                   "punctuation/goodnight3jill.wav","punctuation/goodnight4_jill.wav"]],
        ["Am mallets", ["mallets/Am_Balafon_Enote.wav",
                        "mallets/Am_Bells_Cnote.wav",
                        "mallets/Am_Glock_Gnote.wav",
                        "mallets/Am_Kalimba_hiAnote.wav",
                        "mallets/Am_Marimba_Anote.wav",
                        "mallets/Am_vibes_Cnote.wav"]],
        ["Em mallets", ["mallets/Em_balafon_Enote.wav",
                        "mallets/Em_bells_Cnote.wav",
                        "mallets/Em_glock_Dnote.wav",
                        "mallets/Em_kalimba_Gnote.wav",
                        "mallets/Em_marimba_Enote.wav",
                        "mallets/Em_vibes_Dnote.wav"]],
        ["G mallets", ["mallets/G_balafon_Dnote.wav",
                       "mallets/G_bells_Cnote.wav",
                       "mallets/G_glock_Enote.wav",
                       "mallets/G_kalimba_Gnote.wav",
                       "mallets/G_marimba_Gnote.wav",
                       "mallets/G_vibes_Enote.wav"]],
    ];

    container = document.getElementById("bdiv-2-sound-buttons");
    for(let i=0; i<sounds.length; i++) {
        let b = document.createElement("button");
        b.textContent = sounds[i][0];
        b.className = "btn btn-primary";
        b.style.backgroundColor = "teal"
        b.style.color = "white";
        b.style.margin = "2px";
        b.addEventListener('click', function(event) {
            sendMQTTMessage(
                topic='game-control/runGame/PlaySoundSetAcrossField',
                payload=sounds[i][1].join(',')
            );
        })
        container.appendChild(b);
    }
}

function buildBrightnessSliderRow() {
    rowDiv = document.getElementById("BrightnessSlider");
    let header = document.createElement("span");
    header.textContent = "Field Brightness: "
    rowDiv.appendChild(header);
    for (let brightness = 0; brightness <= 100; brightness+=10) {
        let b = document.createElement("button");
        b.textContent = `${brightness}%`
        b.className = "btn btn-primary";
        b.style.backgroundColor = `hsl(0 0% ${brightness}%)`
        if (brightness <= 60) {
            b.style.color = "white";
        } else {
            b.style.color = "black";
        }
        b.addEventListener('click', function(event) {
            // Brightness on the flowers is a frac8 from 0-255
            let flowerBrightness = Math.round(255 * brightness/100);
            sendMQTTMessage(
                topic='gsa-control/relayToAllFlowersWithThrottling/leds/setBrightness',
                payload=`${flowerBrightness}`);
        })
        rowDiv.appendChild(b);
    }
}

function buildVolumeSliderRow() {
    rowDiv = document.getElementById("VolumeSlider");
    let header = document.createElement("span");
    header.textContent = "Field Volume: "
    rowDiv.appendChild(header);
    for (let volume = 0; volume <= 11; volume+=1) {
        let b = document.createElement("button");
        b.textContent = `${volume}`
        b.className = "btn btn-primary";
        b.style.margin = "8px";
        let volPercentage = volume / 11;
        let fontAdjust = 0.8 + volPercentage * 1.5
        b.style.backgroundColor = "lightgrey"
        b.style.color = "black";
        b.style.fontSize=`${fontAdjust}em`;
        b.addEventListener('click', function(event) {
            sendMQTTMessage(
                topic='gsa-control/relayToAllFlowersWithThrottling/audio/setVolume',
                payload=`${volume}`);
        })
        rowDiv.appendChild(b);
    }
}

function buildHueKeyedButtons(container, headerText, topic, makePayload) {
    let header = document.createElement("span");
    header.textContent = headerText;
    container.appendChild(header);
    for (let hue=0; hue < 255; hue+=32) {
        let b = document.createElement("button");
        b.className = "btn btn-primary";
        b.textContent = hue;
        let hue360 = Math.round(360 * hue/255);
        if (hue == 64) {
            hue360 = 64;  // Correct for FastLED "rainbow" space
        }
        b.style.backgroundColor = `hsl(${hue360} 80% 70%)`;
        b.style.margin = "2px";
        b.addEventListener('click', function(event) {
            sendMQTTMessage(topic=topic, payload=makePayload(hue));
        })
        container.appendChild(b);
    }
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