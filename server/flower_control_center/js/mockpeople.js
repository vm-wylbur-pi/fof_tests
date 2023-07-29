const topic = 'people-locations/'

var mqttmock;

var tracks = {}
var tracksReplay = {}
var replayStartTime
var replayRunning = false
var trackTable

// Ensure that localstorage is configured or initialized when the page loads
let tp = localStorage.getItem('fof-saved-tracks')
if (tp){
    tracks = JSON.parse(tp)
    displayTracks()
}

/********Buttons buttons who's got the buttons*******/
$( "#addTrack-button" ).click(function( event ) {
    let name = $( "#addTrack-name" ).val();
    let description = $( "#addTrack-description" ).val();
    let posx = parseInt($( "#addTrack-x" ).val())
    let posy = parseInt($( "#addTrack-y" ).val())
    tele = addTrack(name, description, {x: posx, y: posy})
    recordTrack(tele.id())
});

$( "#playSelectedTracks-button" ).click(function( event ) {
    //let fps = parseInt($( "#playFPS" ).val());

    if(Object.entries(tracks).length === 0){
        console.log('tracks is empty, replay cancelled')
        return
    }

    clearField()

    let tempTracks = JSON.parse(JSON.stringify(tracks))
    trackTable.getSelectedData().forEach(row => {
        let tn = row['name']
        tracksReplay[tn] = tempTracks[tn]
    })

    replayStartTime = Date.now()
    replayRunning = true
    setInterval(replayTracks,30);
});

$( "#mqtt-reconnect" ).click(function( event ) {
    connectToMQTT();  // Uses the current value of the IP address form field.
});
/******************************************************/



function addTrack(name, description, position = {x:0, y:0}){
    clearField()
    tracks[name] = {
        description: description,
        path: []
    }

    return cy.add({
        group: "nodes",
        data: {
            id: name,
            atype: 'person'
        },
        position: position
    })
}

function recordTrack(id){
    let res = cy.elements('node# ' + id)
    res.on('position',updateTrack)
}

function updateTrack(event){
    // don't record movements if there's a replay going on
    if (replayRunning)
        return true

    let id = event.target.id()
    let pos = event.target.position()

    console.log('id ',id)
    if(tracks[id]['path'].length == 0){
        tracks[id]['enter'] = Date.now()
    }

    // don't record positions outside the field
    //   this is half-baked and guaranteed to generate bugs and weirdness
    if(pos.x < 0 || pos.y < 0){
        tracks[id]['exit'] = Date.now()
    }else {
        let start = tracks[id]['enter']
        tracks[id]['path'].push({
            time: Date.now() - start,
            x: pos.x,
            y: pos.y
        })
    }
    saveTracks()
}

function saveTracks(){
    localStorage.setItem('fof-saved-tracks', JSON.stringify(tracks));
    updateTrackTable()
}

function deleteTrack(name){
    delete tracks[name]
    saveTracks()
}

function clearField(){
   let reles = cy.remove('[atype="person"]')
}

function displayTracks(){
    /*if (Object.keys(tracks).length === 0){
        return
    }*/

    trackTable = new Tabulator("#trackTable", {
        //height:"400px",
        layout:"fitData",
        columns:[
            {title:"Track", field:"name"},
            {title:"Description", field: "description"},
            {title:"Path Length", field: "plen", hozAlign:"center", headerHozAlign: "center"},
            {title:"Delete",
                field: "delete", formatter:"buttonCross", hozAlign:"center", headerHozAlign: "center",
                cellClick:function(e, cell){deleteTrack(cell.getRow().getData()['name'])}
            }
        ],
        data: getTableData(),
        selectable: true
    });
}

function getTableData(){
    let tdata = []
    let i = 0;
    for (var tname in tracks){
        tdata.push({
            id: i,
            name: tname,
            description: tracks[tname]['description'],
            plen: tracks[tname].path.length,
            delete: "X"
        })
        i += 1
    }

    return tdata
}

// tracktable needs time to initialize, and we also need to refresh it
function updateTrackTable(){
    trackTable.replaceData(getTableData())
}


function replayTracks(){
    if(!replayRunning){
        return
    }

    let moveset = {}
    Object.entries(tracksReplay).forEach(function ([id, entry]) {
        let elapsedTime = Date.now() - replayStartTime
        let nextstep = entry['path'][0]['time']
        if (nextstep < elapsedTime){
            let target = entry['path'].shift()
            moveset[id] = {
                'x': target['x'],
                'y': target['y'],
            }
        }
        if(entry['path'].length == 0){
            console.log('end of the line for - ', id)
            delete tracksReplay[id]
        }

        if(Object.keys(tracksReplay) == 0){
            console.log('end of list')
            replayRunning = false
        }
    });

    if (moveset.length == 0) {
        // Don't send empty updates
        return
    }

    let peopleUpdate = {
        'timestamp': Date.now(),
        'people': moveset
    }

    message = new Paho.MQTT.Message(JSON.stringify(peopleUpdate))
    message.destinationName = topic
    mqttmock.send(message)
}

// zomg this should be in a utility function.
function connectToMQTT() {
    let brokerIP = $( "#mqtt-ip" ).val();

    let randomClientNameSuffix = Math.floor(Math.random() * 10000);
    mqttmock = new Paho.MQTT.Client(brokerIP, 9001,
        `Flower_Control_Center_MockPeople_${randomClientNameSuffix}`);

    mqttmock.onConnectionLost = function(context) {
        console.log(`MQTT connection lost: ${context.errorMessage}`)
    };

    var connect_options = {
        timeout: 15,  // seconds
        onSuccess: function() {
            console.log("Mock - Conncted to MQTT Broker.");
        },
        onFailure: function(context) {
            console.log(`MQTT - connection failed: ${context.errorMessage}`);
        }
    }
    mqttmock.connect(connect_options);
}

connectToMQTT()




