$( document ).ready(function() {

    // Send field-level command messages when "Send" is clicked.
    // The GSA is listening for these.
    $( "button#field-level-send" ).click(function (event) {
        let command = $('input[name="field_command"]').val();
        let payload = $('input[name="field_params"]').val();
        sendMQTTMessage(`game-control/${command}`, payload)
    });

    // Buttons to pre-popluate the command form
    // Game command names and parameters are from gsa/mqtt.py
    $( "button#addFairy" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/Fairy");
        $('input[name="field_params"]').val("");
    });
    $( "button#clearFairies" ).click(function (event) {
        $('input[name="field_command"]').val("clearGames");
        $('input[name="field_params"]').val("");
    });
    $( "button#leftToRight" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightHueWave");
        $('input[name="field_params"]').val("160,0,500,600,0");
    });
    $( "button#rightToLeft" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightHueWave");
        $('input[name="field_params"]').val("110,1000,500,-600,0");
    });
    $( "button#bottomToTop" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightHueWave");
        $('input[name="field_params"]').val("200,500,1000,0,-600");
    });
    $( "button#expandingCircle" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/CircularColorWave");
        $('input[name="field_params"]').val("180,500,500,0,600");
    });
    $( "button#contractingCircle" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/CircularColorWave");
        $('input[name="field_params"]').val("20,500,500,500,-600");
    });

});