var cy;

function fetch_field(){

}
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
                selector: 'node',
                style: {
                    'background-image': 'url(/img/daisy.png)',
                    'background-fit': 'cover',
                    'background-color': '#4286f4',
                    width: '40px',
                    height: '40px'
                }
            },
            {
                selector: 'edge',
                style: {
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'curve-style': 'bezier'
                }
            }
        ],
        elements: {
            nodes: [
                { data: { id: 'node1' }, position: { x: 100, y: 100 } },
                { data: { id: 'node2' }, position: { x: 200, y: 200 } }
            ]
        },
        userZoomingEnabled: false,
        panningEnabled: true,
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
});
