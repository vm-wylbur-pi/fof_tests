var cy;

$(document).ready(function() {
    // Identify the div element for the field
    var fieldDiv = $('#field');

    // Configure the height and width of the visualization box
    var boxWidth = 800;
    var boxHeight = 600;

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
                    width: '40px',
                    height: '40px'
                }
            },
            {
                selector: 'node[ftype="poppy"]',
                style: {
                    'background-image': 'url(/img/crocus.png)',
                    'background-fit': 'cover',
                    'background-color': '#4286f4',
                    width: '40px',
                    height: '40px'
                }
            },
            {
                selector: 'node[ftype="geranium"]',
                style: {
                    'background-image': 'url(/img/buttercup.png)',
                    'background-fit': 'cover',
                    'background-color': '#4286f4',
                    width: '40px',
                    height: '40px'
                }
            },
            {
                selector: 'node[ftype="aster"]',
                style: {
                    'background-image': 'url(/img/daisy.png)',
                    'background-fit': 'cover',
                    'background-color': '#4286f4',
                    width: '40px',
                    height: '40px'
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
                  x: res.field.y/-2,
                  y: res.field.x/-2
                },
                group: 'nodes',
                data: {
                    id: 'field',
                    width: res.field.y,
                    height: res.field.x,
                    atype:'field'
                },
                locked: true,
                selectable: false,
                grabbable: false,
                pannable: false
            });

            for (var pid in res.poi) {
                console.log(pid)
                let poi = res.poi[pid]

                let p = cy.add({
                    position: {
                        x: parseInt(poi.x) * -1,
                        y: parseInt(poi.y) * -1
                    },
                    locked: false,
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
                        x: parseInt(flower['y']) * -1,
                        y: parseInt(flower['x']) * -1
                    },
                    locked: true,
                    group: 'nodes',
                    data: {
                        id: fid,
                        sid: flower['sequence'],
                        ftype: flower['type'],
                        height: flower['height'],
                        atype: 'flower'
                    },
                })

                f.on('click', (evt) => {
                    console.log( evt.target.data())
                    $('input[name="flower"]').val(evt.target.data('id'));
                })
            }

            cy.fit(padding = 30)
            cy.minZoom(cy.zoom())
            cy.maxZoom(cy.zoom()+1)
            return res
        })
});
