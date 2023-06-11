var table = new Tabulator("#status-table", {
    //height:"400px",
    layout:"fitData",
    movableRows:true,
    groupBy:"suite",
    //ajaxURL: "/api/state/test/json",
    columns:[
        {title:"Test", field:"test"},
        {title:"Status", field:"status", hozAlign:"center", formatter:"tickCross", width:110},
        {title:"Suite", field:"suite", visible: false},
        {title:"Response", field:"response"}
    ],
});


$.ajax({
    url: '/api/state/test/json',
    success: function(response) {
        table.setData(response)

        var status = true
        for (var ent of JSON.parse(response)){
            if(!ent.status){
                status = false
            }
        }

        let sa = $('#StatusAlert')
        if(status){
            sa.text("ALL TESTS PASSED WOOT");
            sa.css('color', 'green');
        }else{
            sa.text("SOMETHING BROKEN");
            sa.css('color', 'red');
        }
    },
    error: function() {
        console.log('Error occurred during AJAX request to /api/state/test/json');
    }
});


$.ajax({
    url: '/api/state/test/text',
    success: function(response) {
        // Update the content of the div
        let st = $('#StatusText')
        if (response.indexOf("OK") === -1){
            st.text("\n\nTest Results\n" + response);
        }
    },
    error: function() {
        console.log('Error occurred during AJAX request /api/state/test/text.');
    }
});