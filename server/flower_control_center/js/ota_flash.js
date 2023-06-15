function gatherLiveFlowerIPs() {
    let ips = [];
    $( "#flower-table td.ip" ).each(function(index) {
        ips.push($( this ).text());
    });
    return ips;
}

function updateMassOTACommand() {
    let pio_binary_path = $('input[name="pio_binary_path"]').val();
    let flower_code_path = $('input[name="flower_code_path"]').val();
    let flower_ips = gatherLiveFlowerIPs().join(" ");

    let ota_command = `
PLATFORMIO_BINARY=${pio_binary_path}
FLOWER_CODE_DIR=${flower_code_path}
LIVE_FLOWER_IPS="${flower_ips}"

# Run first with no target to build the firmware binary.
\${PLATFORMIO_BINARY} run --project-dir \${FLOWER_CODE_DIR}

# Run in parallel for each live flower to upload the firmware binary.
for ip in \${LIVE_FLOWER_IPS}; do
\${PLATFORMIO_BINARY} run \\
    --project-dir \${FLOWER_CODE_DIR} \\
    --target nobuild \\
    --target upload \\
    --upload-port \${ip} \\
    --silent \\
    &
done
`;
    
    $(' #ota-command-content ').text(ota_command);
}

$( document ).ready(function() {
    $( "#flash-all-flowers-popup" ).hide();

    // Handler to make the OTA command form visible when the "OTA flash all flowers" button is pushed.
    $( "#flash-all-flowers" ).click(function (event) {
        $( "#flash-all-flowers-popup" ).show();
    });

    // Handler to update the content of the OTA command when its parameters are edited.
    $( " .ota_command_param " ).on( "change", function() {
        updateMassOTACommand();
    } );

    $( "#ota_copy_to_clipboard" ).click(function (event) {
        let ota_command = $(' #ota-command-content ').text();
        navigator.clipboard.writeText(ota_command);
    });

});
