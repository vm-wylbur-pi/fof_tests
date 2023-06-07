console.log('sup')


var table = new Tabulator("#status-table", {
    //height:"400px",
    layout:"fitDataColumns",
    movableRows:true,
    groupBy:"suite",
    ajaxURL: "/api/status/json",
    columns:[
        {title:"Test", field:"test"},
        {title:"Status", field:"status", hozAlign:"center", formatter:"tickCross", width:110},
        {title:"Suite", field:"suite", visible: false},
        {title:"Response", field:"response"}
    ],
});

$.ajax({
    url: '/api/status/text',
    success: function(response) {
        // Update the content of the div
        if (response.indexOf("OK") == -1){
            $('#StatusText').text("\n\nTest Results\n" + response);
        }
    },
    error: function() {
        console.log('Error occurred during AJAX request.');
    }
});