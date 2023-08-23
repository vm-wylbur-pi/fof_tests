function populateCommandChoices() {
    const commands = new Map([
        // From multicore/src/comms.cpp
        ["reboot",
         "Reboot this flower. No parameters."],
        ["enterSleepMode",
         "Put this flower into sleep mode. One parameter: milliseconds to sleep"],
        ["time/setEventReference",
         "one integer parameter, seconds since the Unix epoch. Should be in the last couple weeks."],
        ["time/syncWithNTP",
         "No parameters. Re-sync with NTP server on the Feds."],
        ["time/setBPM",
        "one integer parameter. Affects beat-flash tempo."],
        ["leds/listPatterns",
        "Echo the sequence of currently-active LED patterns to the flower's debug stream."],
        ["leds/clearPatterns",
        "Drop all currently-acive LED patterns. Turns the LEDs off.  No parameters."],
        ["leds/removePattern",
        "Remove all instances of the given LED pattern. One param: pattern name, e.g. FairyVisit"],
        ["leds/setBrightness",
        "Set the global brightness of FastLED (via temporal dithering) (0-255). Affects all other patterns."],
        ["leds/addPattern/HuePulse",
        "A surge of color that moves up the flower. Params: hue (0-255), startTime ('+0' for right now), fadeInTime (ms), holdTime (ms), brightness (0-255)"],
        ["leds/addPattern/SatValPulse",
        "A pulsed change in the flower's current saturation & value Params: satChange (0.0-3.0, 1.0 is neutral), valChange (0.0-3.0, 1.0 is neutral), startTime ('+0' for right now), fadeInTime (ms), holdTime (ms)"],
        ["leds/addPattern/FairyVisit",
        "A dancing spot of yellow light.  Two params: visitDuration (ms), fairySpeed (LEDS/sec)"],
        ["leds/addPattern/IndependentIdle",
        "Shifty green leaves and a colored blossom.  No parameters."],
        ["leds/addPattern/Raindrops",
        "Random spots of light appear then fade away. Two parameters: dropsPerSecond, dropFadeTime(ms)"],
        ["leds/addPattern/SolidHue",
        "Make the whole flower (leaves+blossom) one color.  Two params: hue (0-255), startTime ('+0' for right now)"],
        ["leds/addPattern/MaxBrightnessWhite",
        "Full white (255,255,255) with no temporal dithering. leds/setBrightness has no effect when this pattern is active."],
        ["leds/addPattern/RunningDot",
        "A white spot of light that moves up and down the flower. No parameters."],
        ["leds/addPattern/BeatFlash",
        "Flash the whole flower white briefly on each beat.  See time/setBPM.  No parameters."],
        ["leds/updatePattern/Raindrops",
        "Random spots of light appear then fade away. Two parameters: dropsPerSecond, dropFadeTime(ms)"],
        ["leds/updatePattern/BlossomColor",
        "Set the blossom to specified HSVA color. Params all (0-255): hue, saturation, value, alpha (for mixing with earlier patterns)"],
        ["audio/setVolume",
        "One float parameter between 0.0 (mute) and 11.0 (ours go to 11)"],
        ["audio/playSoundFile",
        "One string parameter, the name of sound file. See audio/listSoundFiles for choices"],
        ["audio/stopSoundFile",
        "Stops any on-going sound playback. No parameters."],
        ["audio/listSoundFiles",
        "Echo the first 30 sound files available on the flower to its debug stream."],
        ["audio/toggleMixWithSilence",
        "Whether or not silence data is sent to the audio output in addition to WAV data."],
        ["screen/setText",
        "One string parameter (no commas). Show the given text on the tiny screen in the birdhouse."],
        ["screen/appendText",
        "One string parameter (no commas). Add the given text to whatever is currently shown on the tiny screen."],
        ["screen/resetToFlowerSummary",
        "Show the flower summary info (id, build, network status) on the screen. No parameters."],
    ]);
    commands.forEach((instructions, command) => {
        $('#command-dropDown').append(`<option value="${command}">${command}</option>`);
    });

    $('#command-dropDown').change( function() {
        let command = this.value;
        let instructions = commands.get(command);
        $('#flower_command_param_explanation').text(instructions);
    } );
}

$( document ).ready(function() {
    
    populateCommandChoices();

    $( "span#all" ).on("click", function( event ) {
        $( 'input[name="flower"]' ).val("all");
    });

    $( "#send-command" ).click(function( event ) {
        let targetFlower = $('input[name="flower"]').val();
        let command = $('select[name="command"]').val();
        let payload = $('input[name="parameters"]').val();
        sendMQTTMessage(`flower-control/${targetFlower}/${command}`, payload)
    });

    $( "#send-command-with-throttling" ).click(function( event ) {
        let ignored_targetFlower = $('input[name="flower"]').val();
        let flower_command = $('select[name="command"]').val();
        let payload = $('input[name="parameters"]').val();
        sendMQTTMessage(`gsa-control/relayToAllFlowersWithThrottling/${flower_command}`, payload)
    });

});