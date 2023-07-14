function connectToMQTT() {
    let brokerIP = $( "#mqtt-ip" ).val();
    let randomClientNameSuffix = Math.floor(Math.random() * 10000);
    mqtt = new Paho.MQTT.Client(brokerIP, MQTT_BROKER_PORT,
        `Flower_Control_Center_Field_${randomClientNameSuffix}`);

    mqtt.onConnectionLost = function(context) {
        console.log(`MQTT connection lost: ${context.errorMessage}`)
    };

    mqtt.onMessageArrived = handleMQTTMessage;

    var connect_options = {
        timeout: 15,  // seconds
        onSuccess: function() {
            console.log("Field - Conncted to MQTT Broker.");
            subscribeToPeopleMessages();
        },
        onFailure: function(context) {
            console.log(`MQTT connection failed: ${context.errorMessage}`);
        }
    }
    mqtt.connect(connect_options);
}