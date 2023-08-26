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
    $( "button#clearEffects" ).click(function (event) {
        $('input[name="field_command"]').val("clearGames");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Removes all stateful field-level effects");
    });
    $( "button#resetField" ).click(function (event) {
        $('input[name="field_command"]').val("resetField");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Removes all stateful field-level effects, and reset each flower to IndependentIdle + Raindrops");
    });
    $( "button#randomWaves" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/RandomWaves");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Randomized color waves at randomized intervals, indefinitely.");
    });
    $( "button#mold" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/Mold");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Randomized color waves slowly change the color of the field.");
    });
    $( "button#addFairy" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/Fairy");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Adds one fairy. You can have many. Each is independent of the others.");
    });
    $( "button#rollCall" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/RollCall");
        $('input[name="field_params"]').val("500");
        $('#field_command_param_explanation').text("Each flower lights up and calls 'here', in order across the field. One param: millis between calls.");
    });
    $( "button#aura" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/Aura");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Starts the Aura game. No parameters. It only makes sense to have one instance.");
    });
    $( "button#wave" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/Wave");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Starts the Wave game. No parameters. It only makes sense to have one instance.");
    });
    $( "button#chorusCircle" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/ChorusCircle");
        $('input[name="field_params"]').val("30,5.0");
        $('#field_command_param_explanation').text("Parameters are seconds between song starts and volume (0-11)");
    });
    $( "button#gossip" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/Gossip");
        $('input[name="field_params"]').val("60, 3.0");
        $('#field_command_param_explanation').text("Starts the Gossip game. Parameters are seconds between gossips and volume (0-11)");
    });
    $( "button#funScreenText" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/FunScreenText");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Shows fun messages that occasionally change on the flower screens.");
    });
    $( "button#wind" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/Wind");
        $('input[name="field_params"]').val("");
        $('#field_command_param_explanation').text("Wind gusts from the west that dim the leaves. No parameters yet.");
    });
    $( "button#bouncingBlob" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/BouncingBlob");
        $('input[name="field_params"]').val("200,150");
        $('#field_command_param_explanation').text("A blob of color bouncing aronud.  blobSpeed (inches/sec), blobSize (inches)");
    });
    $( "button#leftToRight" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightColorWave");
        $('input[name="field_params"]').val("160,0,450,600,0,+4000");
        $('#field_command_param_explanation').text("A wave specified by a point and a direction.  hue, startX, startY, velocityX, velocityY, startTime");
    });
    $( "button#rightToLeft" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightColorWave");
        $('input[name="field_params"]').val("110,700,450,-600,0,+4000");
        $('#field_command_param_explanation').text("A wave specified by a point and a direction.  hue, startX, startY, velocityX, velocityY, startTime");
    });
    $( "button#bottomToTop" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightColorWave");
        $('input[name="field_params"]').val("200,350,1000,0,-600,+4000");
        $('#field_command_param_explanation').text("A wave specified by a point and a direction.  hue, startX, startY, velocityX, velocityY, startTime");
    });
    $( "button#topToBottom" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/StraightColorWave");
        $('input[name="field_params"]').val("40,350,0,0,600,+4000");
        $('#field_command_param_explanation').text("A wave specified by a point and a direction.  hue, startX, startY, velocityX, velocityY, startTime");
    });
    $( "button#expandingCircle" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/CircularColorWave");
        $('input[name="field_params"]').val("180,300,450,0,600,+4000");
        $('#field_command_param_explanation').text("A circle that grows or shrinks.  hue, centerX, centerY, startRadius, radiusSpeed, startTime");
    });
    $( "button#contractingCircle" ).click(function (event) {
        $('input[name="field_command"]').val("runGame/CircularColorWave");
        $('input[name="field_params"]').val("20,300,450,500,-600,+4000");
        $('#field_command_param_explanation').text("A circle that grows or shrinks.  hue, centerX, centerY, startRadius, radiusSpeed, startTime");
    });

});