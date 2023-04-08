// FCC management code goes here.

const MQTT_BROKER_IP = "192.168.1.72";
const MQTT_BROKER_PORT = 9001;

// The singlenot Pah.MQTT.Client object.
var mqtt;

function connectToMQTT() {
    console.log("Connecting to MQTT Broker at " + MQTT_BROKER_IP + ":" + MQTT_BROKER_PORT);
    mqtt = new Paho.MQTT.Client(MQTT_BROKER_IP, 9001, "Flower_Control_Center");
    var connect_options = {
        timeout: 2000,
        onSuccess: function() {
            document.write("Conncted to MQTT Broker.")
        }
    }
    mqtt.connect(connect_options);
}

$( document ).ready(function() {
    connectToMQTT();
});
