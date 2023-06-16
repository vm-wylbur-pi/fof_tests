import paho.mqtt.client as paho_mqtt
import games
from geometry import Point, Vector

# Used during development.
# TODO: Read this from config
MQTT_BROKER_IP = "127.0.0.1"

def SetupMQTTClient(gameState):
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
        HandleMQTTMessage(message, gameState)

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


def HandleMQTTMessage(message, gameState):
    _, command = message.topic.split('/', maxsplit=1)
    params = message.payload.decode().split(',')

    if command == "clearGames":
        gameState.clearStatefulGames()
        return

    if command == "runGame/StraightHueWave":
        hue = 160 if len(params) < 1 else int(params[0])
        startX = 500 if len(params) < 2 else int(params[1])
        startY = 500 if len(params) < 3 else int(params[2])
        velocityX = 300 if len(params) < 4 else int(params[3])
        velocityY = 0 if len(params) < 5 else int(params[4])
        wave = games.StraightColorWave(hue,
                                    start_loc=Point(startX, startY),
                                    velocity=Vector(velocityX, velocityY))
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/CircularColorWave":
        hue = 160 if len(params) < 1 else int(params[0])
        centerX = 500 if len(params) < 2 else int(params[1])
        centerY = 500 if len(params) < 3 else int(params[2])
        startRadius = 0 if len(params) < 4 else int(params[3])
        speed = 300 if len(params) < 5 else int(params[4])
        wave = games.CircularColorWave(hue, center=Point(centerX, centerY),
                                       startRadius=startRadius, speed=speed)
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/Fairy":
        # No parameters (yet) for the fairy game.  It runs indefinitely.
        gameState.runStatefulGame(games.Fairy())
        return

    print(f"Unhandled command: {command}({message.payload.decode()})")
