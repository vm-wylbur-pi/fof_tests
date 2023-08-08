import paho.mqtt.client as paho_mqtt
from geometry import Point, Vector

import gsa.games.aura as aura
import gsa.games.wave as wave_module
import gsa.games.color_waves as color_waves
import gsa.games.fairy as fairy
import gsa.games.fun_screen_text as fun_screen_text
import gsa.games.sleep_mode as sleep_mode

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
        print('Subscribing to people location updates.')
        client.subscribe("people-locations/#")
        print('Subscribing to reference clock updates.')
        client.subscribe("flower-control/all/time/setEventReference")

    def on_message(unused_client, unused_userdata, message):
        HandleMQTTMessage(message, gameState)

    def on_disconnect(client, unused_userdata, result_code):
        if result_code != 0:
            print("Unexpected MQTT disconnection.")
            print(f"Client connected?: {client.is_connected()}")

    client = paho_mqtt.Client(client_id="gsa")
    client.on_pre_connect = on_pre_connect
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    # I'm not sure if this is helpful yet.
    client.reconnect_delay_set(min_delay=1, max_delay=5)  # time unit is seconds
    client.connect(MQTT_BROKER_IP)

    # Flowers get a reference to the client, because sending the mqtt commands needed
    # for running games is delegated to each of them.
    for flower in gameState.flowers:
        flower.mqtt_client = client

    # Caller is responsible for calling client.loop() to handle received messages
    return client


def HandleMQTTMessage(message, gameState):
    if message.topic.startswith("game-control"):
        HandleGameControlCommand(message, gameState)
    elif message.topic.startswith("people-locations"):
        gameState.people.updateFromMQTT(message)
    elif message.topic.startswith("flower-control/all/time/setEventReference"):
        # flower-control/*/time/setEventReference has a single integer parameter
        gameState.control_timer_reference_time = int(message.payload)
        print(f"Set event reference time to {gameState.control_timer_reference_time}")
    else:
        print(f"Unhandled MQTT message topic: {message.topic}")


def HandleGameControlCommand(message, gameState):
    _, command = message.topic.split('/', maxsplit=1)
    raw_param_string = message.payload.decode()
    params = raw_param_string.split(',') if raw_param_string else []
    print(f"Received command: {command}({','.join(params)})")

    if command == "clearGames":
        gameState.clearStatefulGames()
        return

    if command == "runGame/StraightColorWave":
        wave = color_waves.StraightColorWave.randomInstance(gameState.field)
        if len(params) >= 1:
            wave.hue = int(params[0])
        if len(params) >= 3:
            wave.start_loc = Point(int(params[1]), int(params[2]))
        if len(params) >= 5:
            wave.velocity = Vector(int(params[3]), int(params[4]))
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/CircularColorWave":
        wave = color_waves.CircularColorWave.randomInstance(gameState.field)
        if len(params) >= 1:
            wave.hue = int(params[0])
        if len(params) >= 3:
            wave.center = Point(int(params[1]), int(params[2]))
        if len(params) >= 4:
            wave.startRadius = int(params[3])
        if len(params) >= 5:
            wave.speed = int(params[4])
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/Aura":
        gameState.runStatefulGame(aura.Aura())
        return

    if command == "runGame/Wave":
        gameState.runStatefulGame(wave_module.Wave())
        return

    if command == "runGame/Fairy":
        # No parameters (yet) for the fairy game.  It runs indefinitely.
        gameState.runStatefulGame(fairy.Fairy())
        return

    if command == "runGame/RandomIdle":
        gameState.runStatefulGame(color_waves.RandomIdle())
        return

    if command == "runGame/FunScreenText":
        gameState.runStatefulGame(fun_screen_text.FunScreenText())
        return

    print(f"Unhandled command: {command}({message.payload.decode()})")
