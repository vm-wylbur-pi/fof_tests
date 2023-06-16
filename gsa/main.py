# TODO: docs, what is the GSA?
import time
import threading

import flower
import mqtt
import games
from geometry import Point, Vector

mqtt_client = mqtt.SetupMQTTClient()

flowers = flower.readFieldFromDeploymentYAML("../fake_field/jeffs_living_room_deployment.yaml")

# TODO: There is probably better way to share the mqtt client handle
for flower in flowers:
    flower.mqtt_client = mqtt_client

stateful_games = []

# For monitoring keyborad commands without blocking the main game loop
class KeyboardInputThread(threading.Thread):
    def __init__(self, callback):
        self.callback = callback
        super(KeyboardInputThread, self).__init__(name='gsa-input-thread')
        self.start()

    def run(self):
        while True:
            self.callback(input("Next command? "))

def handle_keyboard_input(command):
    global stateful_games
    if command == "x":
        # Clear all current-running games
        stateful_games = []
    elif command == "a":
        # A single left-to-right wave
        games.StraightColorWave(120, start_loc=Point(100,100), velocity=Vector(500,0)).run(flowers)
    elif command == "b":
        # Left-to-right wave superimposed on top-to-bottom wave
        games.StraightColorWave(120, start_loc=Point(100, 100), velocity=Vector(500, 0)).run(flowers)
        games.StraightColorWave(200, start_loc=Point(100, 100), velocity=Vector(0, 400)).run(flowers)
    elif command == "c":
        stateful_games.append(games.Fairy())

input_thread = KeyboardInputThread(handle_keyboard_input)

# Interaction/game loop
while True:

    # Update the current set of stateful games
    stateful_games = [g for g in stateful_games if not g.isDone()]
    for game in stateful_games:
        game.runLoop(flowers)

    # Check for any mqtt messages, and send any buffered outgoing messages
    if not mqtt_client.is_connected():
        mqtt_client.reconnect()
    mqtt_client.loop()

    # We may want something like this later. For now, the input() call at the top stalls the loop.
    time.sleep(1/60)  # seconds
