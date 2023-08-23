var cy;

$(document).ready(function() {

    // default for people topic
    var people_topic = "people-locations/"

    // Identify the div element for the field
    var fieldDiv = $('#field');

    // Configure the height and width of the visualization box
    var boxWidth = 700;
    var boxHeight = 400;

    // Set the dimensions of the visualization box
    fieldDiv.width(boxWidth);
    fieldDiv.height(boxHeight);

    // Create the cytoscape visualization within the field div
    cy = cytoscape({
        container: fieldDiv,
        style: [
            {
                selector: 'node[atype="flower"][^ftype]',
                style: {
                    'label': '???',
                    'background-color': 'white',
                    width: '75px',
                    height: '75px'
                }
            },
            {
              selector: 'node[atype="person"]',
              style: {
                  'label': 'data(id)',
                  'shape': 'square',
                  'font-size': '50px',
                  width: '75px',
                  height: '75px'
              }
            },
            {
                selector: 'node[ftype="poppy"]',
                style: {
                    'background-image': 'url(/img/crocus.png)',
                    'background-fit': 'cover',
                    'background-color': '#4286f4',
                    width: '75px',
                    height: '75px'
                }
            },
            {
                selector: 'node[ftype="geranium"]',
                style: {
                    'background-image': 'url(/img/buttercup.png)',
                    'background-fit': 'cover',
                    'background-color': '#4286f4',
                    width: '75px',
                    height: '75px'
                }
            },
            {
                selector: 'node[ftype="aster"]',
                style: {
                    'background-image': 'url(/img/daisy.png)',
                    'background-fit': 'cover',
                    'background-color': '#4286f4',
                    width: '75px',
                    height: '75px'
                }
            },
            {
                selector: 'node[id="field"]',
                style: {
                    'width': 'data(width)',
                    'height': 'data(height)',
                    'shape': 'square',
                    'background-opacity': .4,
                    'border-color': 'black',
                }
            },
            {
                selector: 'node[ptype="rectangle"]',
                style: {
                    'width': 'data(width)',
                    'height': 'data(height)',
                    'shape': 'square',
                    'background-opacity': .8,
                    'border-color': 'blue',
                    'label': 'data(name)'
                }
            }
        ],
        userZoomingEnabled: true,
        boxSelectionEnabled: false
    });
    // demo your core ext
    cy.gridGuide({
        gridSpacing: 100, // Distance between the lines of the grid.
        snapToGridOnRelease: false,
        snapToGridCenter: false,
        guidelinesStyle: {
            strokeStyle: "black",
            horizontalDistColor: "#ff0000",
            verticalDistColor: "green",
            initPosAlignmentColor: "#0000ff",
        }
    });

   var deployment =  $.ajax({url:'/api/config/deployment'})
        .then( res => {
            let field = cy.add({
                position: {
                  x: res.field.x/2,
                  y: res.field.y/2
                },
                group: 'nodes',
                data: {
                    id: 'field',
                    width: res.field.x,
                    height: res.field.y,
                    atype:'field'
                },
                locked: true,
                selectable: false,
                grabbable: false,
                pannable: false
            });

            for (var pid in res.poi) {
                let poi = res.poi[pid]
                let p = cy.add({
                    position: {
                        x: parseInt(poi.x),
                        y: parseInt(poi.y)
                    },
                    locked: true,
                    group: 'nodes',
                    data: {
                        name: pid,
                        ptype: poi.ptype,
                        width: poi.width,
                        height: poi.height,
                        atype: 'poi'
                    }

                })
            }

            for (var fid in res.flowers) {
                let flower = res.flowers[fid]
                let position

                let f = cy.add({
                    position: {
                        x: parseInt(flower['x']),
                        y: parseInt(flower['y'])
                    },
                    locked: false,
                    group: 'nodes',
                    data: {
                        id: fid,
                        sid: flower['sequence'],
                        ftype: flower['type'],
                        height: flower['height'],
                        atype: 'flower',
                        x: flower['x'],
                        y: flower['y']
                    },
                })

                f.on('click', (evt) => {
                    d = evt.target.data()
                    d['px'] = evt.target.position('x')
                    d['py'] = evt.target.position('y')
                    $('input[name="flower"]').val(evt.target.data('id'));
                    console.log(evt.target.data())
                    let pos = evt.target.data('id') + ' x: ' + evt.target.data('x') + ' , y: ' + evt.target.data('y')
                    $('#clickfield').html(pos)
                })
            }

            cy.fit(padding = 30)
            cy.minZoom(0.2)
            cy.maxZoom(5)
            return res
        })

    function subscribeToPeopleMessages() {
       mqtt.subscribe(people_topic, {
           onSuccess: () => {
               console.log('Field - Subscribed to people topic')
           },
           onFailure: (res) => {
               console.log('Field - lost subscription' + res.errorMessage)
           }
       })
    }

    function handleMQTTMessage(message) {
        if (message.destinationName.startsWith(people_topic)) {
            let mparse = JSON.parse(message.payloadString)
            handlePeople(mparse['people'])
        }
    }

    function handlePeople(plist){
       let foundpeople = cy.collection()

        let peeps = cy.nodes('[atype="person"]')
        // just remove everyone and re-draw rather than diff
        cy.remove(peeps)

        for (var pid in plist){
            var pobj = plist[pid]
            var pele = cy.$id(pid)
            if(pele.length == 0){
                pele = cy.add({
                    id: pid,
                    data: {
                        id: pid,
                        atype: 'person'
                    }
                })
            }

            pele.position({x: pobj['x'], y: pobj['y']})
            foundpeople.add(pele)
        }
        // clean out people who weren't in the list
        //let ediff = cy.nodes('[atype="person"]').diff(foundpeople)
        //console.log(ediff.left.length, ediff.right.length)
        //console.log(foundpeople)
        //cy.remove(unfoundpeople)
    }

    function connectToMQTT() {
        let brokerIP = $( "#mqtt-ip" ).val();

        let randomClientNameSuffix = Math.floor(Math.random() * 10000);
        mqtt = new Paho.MQTT.Client(brokerIP, 9001,
            `Flower_Control_Center_Field_${randomClientNameSuffix}`);

        mqtt.onConnectionLost = function(context) {
            console.log(`MQTT connection lost: ${context.errorMessage}`)
        };

        mqtt.onMessageArrived = handleMQTTMessage;

        var connect_options = {
            timeout: 15,  // seconds
            reconnect: true,
            onSuccess: function() {
                console.log("Field - Conncted to MQTT Broker.");
                subscribeToPeopleMessages();
            },
            onFailure: function(context) {
                console.log(`MQTT connection failed: ${context.errorMessage}`);
            }
        }
        mqtt.connect(connect_options);
    }

    connectToMQTT()
});
