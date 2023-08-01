import paho.mqtt.client as mqtt

import fake_flowers

# Used during development.
# TODO: Read this from config
MQTT_BROKER_IP = "127.0.0.1"

def SetupMQTTClient(flowers, people):
    # Required by paho, but unused
    def on_pre_connect(unused_arg1, unused_arg2):
        pass

    def on_connect(client, unused_userdata, unused_flags, result_code):
        result = "successfull." if result_code == 0 else "FAILED!"
        print(f'Connection to MQTT broker at {MQTT_BROKER_IP} {result}')
        # hashtag is the MQTT wildcard. This subscribes to flower-control/all/... messages,
        # which will be relayed to the full field, and to flower-control/<ID>/... messages,
        # which will be relayed to a single flower.
        print('Subscribing to flower control messages.')
        client.subscribe("flower-control/#")
        print('Subscribing to people location updates.')
        client.subscribe("people-locations/#")

    def on_message(unused_client, unused_userdata, message):
        # print(f"Received message, topic='{message.topic}', content='{message.payload}'")
        if message.topic.startswith("flower-control"):
            send_commands_to_flowers(message, flowers)
        elif message.topic.startswith("people-locations"):
            people.updateLocations(message)
        else:
            print(f"Unhandled MQTT message topic: {message.topic}")

    def on_disconnect(unused_client, unused_userdata, result_code):
        if result_code != 0:
            print("Unexpected MQTT disconnection.")

    client = mqtt.Client(client_id="fake_flowers")
    client.on_pre_connect = on_pre_connect
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    # I'm not sure if this is helpful yet.
    # client.reconnect_delay_set(min_delay=1, max_delay=120)  # time unit is seconds
    client.connect(MQTT_BROKER_IP)

    # Caller is responsible for calling client.loop() to handle received messages
    return client


def send_commands_to_flowers(mqtt_message, flowers):
    # Here, I see which flower(s) are the recipent based on the message topic, 
    # then I make method calls to the fake flowers that are analogous to MQTT
    # commands received by the real flowers.
    unused_flower_control, which_flower, command = mqtt_message.topic.split("/", maxsplit=2)
    payload = mqtt_message.payload.decode('utf-8')

    if command == "time/setEventReference":
        # "flower-control/*/time/setEventReference" has a single integer parameter
        new_reference_time = int(payload)
        for flower in flowers:
            if flower.id == which_flower or which_flower == "all":
                flower.setEventReference(new_reference_time)

    elif command == "leds/clearPatterns":
        for flower in flowers:
            if flower.id == which_flower or which_flower == "all":
                flower.clearPatterns()

    elif command.startswith("leds/addPattern"):
        unused_leds, unused_addPattern, pattern_name = command.split('/')
        pattern_params = payload
        for flower in flowers:
            if flower.id == which_flower or which_flower == "all":
                flower.addPattern(pattern_name, pattern_params)

    elif command.startswith("audio/playSoundFile"):
        audio_filename = payload
        for flower in flowers:
            if flower.id == which_flower or which_flower == "all":
                flower.showText(audio_filename)

    elif command.startswith("screen/setText"):
        text_to_show_on_screen = payload
        for flower in flowers:
            if flower.id == which_flower or which_flower == "all":
                flower.showText(text_to_show_on_screen, duration=20000)

    else:
        print(f"Flower command {command} isn't implemented by fake_field.")
        return
