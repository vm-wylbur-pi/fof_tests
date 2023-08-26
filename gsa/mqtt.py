from collections import deque
from dataclasses import dataclass

import paho.mqtt.client as paho_mqtt
from geometry import Point, Vector

import gsa.games.aura as aura
import gsa.games.bouncing_blob as bouncing_blob
import gsa.games.wave as wave_module
import gsa.games.chorus_circle as chorus_circle
import gsa.games.color_waves as color_waves
import gsa.games.fairy as fairy
import gsa.games.gossip as gossip
import gsa.games.fun_screen_text as fun_screen_text
import gsa.games.roll_call as roll_call
import gsa.games.sleep_mode as sleep_mode
import gsa.games.wind as wind

# Used during development.
# TODO: Read this from config
MQTT_BROKER_IP = "192.168.1.72"

# A throttler to prevent sending too many MQTT messages to the flowers at once.
# We've seen that sending more than about 40 at a time can cause wifi congestion
class MQTTThrottler:
    def __init__(self, mqtt_client, maxPerGSAFrame=20):
        self.mqtt_clinet = mqtt_client
        self.maxPerGSAFrame = maxPerGSAFrame
        self.numThisFrame = 0
        self.buffer = deque()

    @dataclass
    class Message:
        topic: str
        payload: str
        retain: bool
        qos: int

    def sendMessage(self, topic: str, payload: str, retain: bool = False, qos: int=0):
        if self.numThisFrame < self.maxPerGSAFrame:
            self.mqtt_clinet.publish(topic=topic, payload=payload, retain=retain, qos=qos)
            self.numThisFrame += 1
        else:
            self.buffer.append(MQTTThrottler.Message(topic, payload, retain, qos))

    def resetMessageCount(self):
        self.numThisFrame = 0
        while self.buffer and self.numThisFrame < self.maxPerGSAFrame:
            msg: MQTTThrottler.Message = self.buffer.popleft()
            self.mqtt_clinet.publish(topic=msg.topic, payload=msg.payload,
                                     retain=msg.retain, qos=msg.qos)
            self.numThisFrame += 1
        if self.buffer:
            print(f"MQTT Throttler has {len(self.buffer)} messages unsent this frame.")


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
        print('Subscribing to GSA-control messages')
        client.subscribe("gsa-control/#")
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
    flowerMessageThrottler = MQTTThrottler(client, maxPerGSAFrame=20)
    for flower in gameState.flowers:
        flower.mqttThrottler = flowerMessageThrottler
    gameState.mqttThrottler = flowerMessageThrottler

    # Caller is responsible for calling client.loop() to handle received messages
    return client


def HandleMQTTMessage(message, gameState):
    if message.topic.startswith("game-control"):
        HandleGameControlCommand(message, gameState)
    elif message.topic.startswith("gsa-control"):
        HandleGSAControlCommand(message, gameState)
    elif message.topic.startswith("people-locations"):
        gameState.people.updateFromMQTT(message)
    elif message.topic.startswith("flower-control/all/time/setEventReference"):
        # flower-control/*/time/setEventReference has a single integer parameter
        # It is seconds since the epoch.
        gameState.control_timer_reference_time = int(message.payload)
        print(f"Set event reference time to {gameState.control_timer_reference_time}")
        print(f"Control timer is {gameState.controlTimer()}")
    else:
        print(f"Unhandled MQTT message topic: {message.topic}")


def HandleGSAControlCommand(message, gameState):
    _, command = message.topic.split('/', maxsplit=1)
    raw_param_string = message.payload.decode()
    params = raw_param_string.split(',') if raw_param_string else []
    print(f"Received GSA command: {command}({','.join(params)})")

    if command.startswith("relayToAllFlowersWithThrottling"):
        _, flower_command = command.split('/', maxsplit=1)
        print(f"Relaying command to all flowers: {flower_command}({raw_param_string})")
        for flower in gameState.flowers:
            flower.sendMQTTCommand(flower_command, raw_param_string)
        return

    if command == "playSoundNearPoint":
        if len(params) < 3:
            print("Not enough parameters to playSoundNearPoint")
            return
        sound, x, y = params[0], int(params[1]), int(params[2])
        closestFlower = gameState.closestFlowerTo(Point(x,y))
        print(f"Playing {sound} near {x},{y} (chose flower {closestFlower.num})")
        closestFlower.PlaySoundFile(sound)
        return
    
    if command == "sendHeartbeat":
        gameState.sendHeartbeat()
        return
    
    print(f"Unhandled gsa-control command: {command}({message.payload.decode()})")


def HandleGameControlCommand(message, gameState):
    _, command = message.topic.split('/', maxsplit=1)
    raw_param_string = message.payload.decode()
    params = raw_param_string.split(',') if raw_param_string else []
    print(f"Received game command: {command}({','.join(params)})")

    if command == "clearGames":
        gameState.clearStatefulGames()
        return

    if command == "resetField":
        gameState.clearStatefulGames()
        for flower in gameState.flowers:
            flower.sendMQTTCommand("leds/clearPatterns", params="")
            flower.sendMQTTCommand("leds/addPattern/IndependentIdle", params="")
            flower.sendMQTTCommand("leds/addPattern/Raindrops", params="5,3")
        return

    if command == "runGame/StraightColorWave":
        wave = color_waves.StraightColorWave.randomInstance(gameState)
        if len(params) >= 1:
            wave.hue = int(params[0])
        if len(params) >= 3:
            wave.start_loc = Point(int(params[1]), int(params[2]))
        if len(params) >= 5:
            wave.velocity = Vector(int(params[3]), int(params[4]))
        if len(params) >= 6:
            wave.startTime = gameState.parseStartTime(params[5])
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/StraightSatValWave":
        wave = color_waves.StraightSatValWave.randomInstance(gameState)
        if len(params) >= 1:
            wave.satChange = float(params[0])
        if len(params) >= 2:
            wave.valChange = float(params[1])
        if len(params) >= 4:
            wave.start_loc = Point(int(params[2]), int(params[3]))
        if len(params) >= 6:
            wave.velocity = Vector(int(params[4]), int(params[5]))
        if len(params) >= 7:
            wave.startTime = gameState.parseStartTime(params[6])
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/CircularColorWave":
        wave = color_waves.CircularColorWave.randomInstance(gameState)
        if len(params) >= 1:
            wave.hue = int(params[0])
        if len(params) >= 3:
            wave.center = Point(int(params[1]), int(params[2]))
        if len(params) >= 4:
            wave.startRadius = int(params[3])
        if len(params) >= 5:
            wave.speed = int(params[4])
        if len(params) >= 6:
            wave.startTime = gameState.parseStartTime(params[5])
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/CircularStickyColorWave":
        wave = color_waves.CircularStickyColorWave.randomInstance(gameState)
        if len(params) >= 1:
            wave.hue = int(params[0])
        if len(params) >= 3:
            wave.center = Point(int(params[1]), int(params[2]))
        if len(params) >= 4:
            wave.startRadius = int(params[3])
        if len(params) >= 5:
            wave.speed = int(params[4])
        if len(params) >= 6:
            wave.startTime = gameState.parseStartTime(params[5])
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/CircularSatValWave":
        wave = color_waves.CircularSatValWave.randomInstance(gameState)
        if len(params) >= 1:
            wave.satChange = float(params[0])
        if len(params) >= 2:
            wave.valChange = float(params[1])
        if len(params) >= 4:
            wave.center = Point(int(params[2]), int(params[3]))
        if len(params) >= 5:
            wave.startRadius = int(params[4])
        if len(params) >= 6:
            wave.speed = int(params[5])
        if len(params) >= 7:
            wave.startTime = gameState.parseStartTime(params[6])
        gameState.runStatelessGame(wave)
        return

    if command == "runGame/Aura":
        gameState.runStatefulGame(aura.Aura())
        return

    if command == "runGame/Mold":
        gameState.runStatefulGame(color_waves.Mold())
        return

    if command == "runGame/Wind":
        # TODO: expose some parameters, like wind direction from N S E W
        gameState.runStatefulGame(wind.Wind())
        return

    if command == "runGame/Wave":
        gameState.runStatefulGame(wave_module.Wave())
        return

    if command == "runGame/ChorusCircle":
        gapBetweenSongsSecs = 60
        volume = 5.0
        if len(params) >= 1:
            gapBetweenSongsSecs = int(params[0])
        if len(params) >= 2:
            volume = float(params[1])
        gameState.runStatefulGame(chorus_circle.ChorusCircle(gapBetweenSongsSecs, volume))
        return

    if command == "runGame/Gossip":
        gapBetweenGossipsSecs = 60
        volume = 3.0
        if len(params) >= 1:
            gapBetweenGossipsSecs = int(params[0])
        if len(params) >= 2:
            volume = float(params[1])
        gameState.runStatefulGame(gossip.Gossip(gapBetweenGossipsSecs, volume))
        return

    if command == "runGame/Fairy":
        # No parameters (yet) for the fairy game.  It runs indefinitely.
        gameState.runStatefulGame(fairy.Fairy())
        return

    if command == "runGame/BouncingBlob":
        blobSpeed = 200  # inches per second
        blobRadius = 150  # inches
        if len(params) >= 1:
            blobSpeed = int(params[0])
        if len(params) >= 2:
            blobRadius = int(params[1])
        gameState.runStatefulGame(bouncing_blob.BouncingBlob(blobSpeed, blobRadius))
        return

    if command == "runGame/RollCall":
        gapBetweenCallsMillis = 500
        if len(params) >= 1:
            gapBetweenCallsMillis = int(params[0])
        gameState.runStatefulGame(roll_call.RollCall(gapBetweenCallsMillis))
        return

    if command == "runGame/RandomWaves":
        gameState.runStatefulGame(color_waves.RandomWaves())
        return

    if command == "runGame/FunScreenText":
        gameState.runStatefulGame(fun_screen_text.FunScreenText())
        return

    print(f"Unhandled command: {command}({message.payload.decode()})")
