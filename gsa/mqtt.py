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
    raw_param_string = message.payload.decode()
    params = raw_param_string.split(',') if raw_param_string else []
    print(f"Command is {command}{params}")

    if command == "clearGames":
        gameState.clearStatefulGames()
        return

    if command == "runGame/StraightColorWave":
        wave = games.StraightColorWave.randomInstance(gameState.field)
        if len(params) >= 1:
            wave.hue = int(params[0])
        if len(params) >= 2:
            wave.startX = int(params[1])
        if len(params) >= 3:
            wave.startY = int(params[2])
        if len(params) >= 4:
            wave.velocityX = int(params[3])
        if len(params) >= 5:
            wave.velocityY = int(params[4])
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/CircularColorWave":
        wave = games.CircularColorWave.randomInstance(gameState.field)
        if len(params) >= 1:
            wave.hue = int(params[0])
        if len(params) >= 2:
            wave.centerX = int(params[1])
        if len(params) >= 3:
            wave.centerY = int(params[2])
        if len(params) >= 4:
            wave.startRadius = int(params[3])
        if len(params) >= 5:
            wave.speed = int(params[4])
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/Fairy":
        # No parameters (yet) for the fairy game.  It runs indefinitely.
        gameState.runStatefulGame(games.Fairy())
        return

    if command == "runGame/RandomIdle":
        gameState.runStatefulGame(games.RandomIdle())
        return

    if command == "runGame/FunScreenText":
        gameState.runStatefulGame(games.FunScreenText())
        return

    print(f"Unhandled command: {command}({message.payload.decode()})")
