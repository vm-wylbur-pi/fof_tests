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
            }
        ],
        userZoomingEnabled: true,
        boxSelectionEnabled: false
    });
    // demo your core ext
    cy.gridGuide({
        guidelinesStyle: {
            strokeStyle: "black",
            horizontalDistColor: "#ff0000",
            verticalDistColor: "green",
            initPosAlignmentColor: "#0000ff",
        }
    });

   var deployment =  $.ajax({url:'/api/state/cache/deployment'})
        .then( res => {
            let n = cy.add({
                position: {
                  x: res.field.dimensions.x*5,
                  y: res.field.dimensions.y*5
                },
                group: 'nodes',
                data: {
                    id: 'field',
                    ntype: 'field',
                    width: res.field.dimensions.x*10,
                    height: res.field.dimensions.y*10
                },
                locked: true,
                selectable: false,
                grabbable: false,
                pannable: true
            });
            n.style('z-index',0)
            cy.fit(padding = 30)
            cy.minZoom(cy.zoom())
            return res
        })
        .then(d => {
            return $.ajax({url:'/api/state/cache/flowers'})
                .then( res => {
                    let de = cy.$id('field')
                    let d = de.data()
                    for(var fid in res){
                        let flower = res[fid]

                        let position
                        if (flower['position']){
                            position = {
                                x: flower['position']['x'] * 10,
                                y: flower['position']['y'] * 10
                            }
                        }else {
                            position = {x: 0, y:0}
                        }

                        let n = cy.add({
                            position: position,
                            locked: true,
                            group: 'nodes',
                            data: {
                                id: fid,
                                sid: flower['sequence'],
                                ftype: flower['flower_type'],
                                height: flower['height']
                            },
                        })
                        n.style('z-index',1)
                    }
                    cy.zoomingEnabled(true)
                    cy.panningEnabled(true)
                })
        })
});
