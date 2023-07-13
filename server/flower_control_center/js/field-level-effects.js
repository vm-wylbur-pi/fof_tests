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
        $('#field_command_param_explanation').text("Adds one fairy. You can have many. Each is independent of the othres.");
    });
    $( "button#clearFairies" ).click(function (event) {
        $('input[name="field_command"]').val("clearGames");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Removes all stateful effects (currently that's just Fairy instances.)");
    });
    $( "button#leftToRight" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightColorWave");
        $('input[name="field_params"]').val("160,0,450,600,0");
        $('#field_command_param_explanation').text("A wave specified by a point and a direction.  hue, startX, startY, velocityX, velocityY");
    });
    $( "button#rightToLeft" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightColorWave");
        $('input[name="field_params"]').val("110,700,450,-600,0");
        $('#field_command_param_explanation').text("A wave specified by a point and a direction.  hue, startX, startY, velocityX, velocityY");
    });
    $( "button#bottomToTop" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightColorWave");
        $('input[name="field_params"]').val("200,350,1000,0,-600");
        $('#field_command_param_explanation').text("A wave specified by a point and a direction.  hue, startX, startY, velocityX, velocityY");
    });
    $( "button#topToBottom" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightColorWave");
        $('input[name="field_params"]').val("40,350,0,0,600");
        $('#field_command_param_explanation').text("A wave specified by a point and a direction.  hue, startX, startY, velocityX, velocityY");
    });
    $( "button#expandingCircle" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/CircularColorWave");
        $('input[name="field_params"]').val("180,300,450,0,600");
        $('#field_command_param_explanation').text("A circle that grows or shrinks.  hue, centerX, centerY, startRadius, radiusSpeed");
    });
    $( "button#contractingCircle" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/CircularColorWave");
        $('input[name="field_params"]').val("20,300,450,500,-600");
        $('#field_command_param_explanation').text("A circle that grows or shrinks.  hue, centerX, centerY, startRadius, radiusSpeed");
    });

});