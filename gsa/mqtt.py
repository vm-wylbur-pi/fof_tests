import paho.mqtt.client as paho_mqtt

# Used during development.
# TODO: Read this from config
MQTT_BROKER_IP = "127.0.0.1"

def SetupMQTTClient():
    # Required by paho, but unused
    def on_pre_connect(unused_arg1, unused_arg2):
        pass

    def on_connect(client, unused_userdata, unused_flags, result_code):
        result = "successfull." if result_code == 0 else "FAILED!"
        print(f'Connection to MQTT broker at {MQTT_BROKER_IP} {result}')
        # hashtag is the MQTT wildcard.
        print('Subscribing to game control messages')
        client.subscribe("game-control/#")

    def on_message(unused_client, unused_userdata, message):
        print(f"Received message, topic='{message.topic}', content='{message.payload}'")
        print("TODO: add message handling code.")

    def on_disconnect(unused_client, unused_userdata, result_code):
        if result_code != 0:
            print("Unexpected MQTT disconnection.")

    client = paho_mqtt.Client(client_id="gsa")
    client.on_pre_connect = on_pre_connect
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    # I'm not sure if this is helpful yet.
    # client.reconnect_delay_set(min_delay=1, max_delay=120)  # time unit is seconds
    client.connect(MQTT_BROKER_IP)

    # Caller is responsible for calling client.loop() to handle received messages
    return client


