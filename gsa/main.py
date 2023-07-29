# TODO: docs, what is the GSA?
import time
import threading

import flower
import field
import mqtt
import games
from geometry import Point, Vector

DEPLOYMENT_FILE = "../fake_field/lucas_party_deployment.yaml"

# Wrapper for references to the game state.
class GameState:
    def __init__(self):
        self.flowers = flower.readFlowersFromDeploymentYAML(DEPLOYMENT_FILE)
        self.field = field.Field(DEPLOYMENT_FILE)
        self.stateful_games = []

    def runStatelessGame(self, game):
        game.run(self.flowers)

    def runStatefulGame(self, game):
        self.stateful_games.append(game)

    def clearStatefulGames(self):
        for game in self.stateful_games:
            game.stop(self.flowers)
        self.stateful_games = []

    def updateStatefulGames(self):
        self.stateful_games = [g for g in self.stateful_games if not g.isDone()]
        for game in self.stateful_games:
            game.runLoop(self.flowers, self.field)

gameState = GameState()
# The mqtt client gets a reference to the game state so that:
#  1) it can pass it on to each flower object. The flower objects each can send
#     mqtt messages to the real-world flowers they represent
#  2) it can be used in the callbacks that respond to person location
#     updates (currently sent over MQTT)
mqtt_client = mqtt.SetupMQTTClient(gameState)

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
        gameState.clearStatefulGames()
    elif command == "w":
        # A randomized straight-line wave.
        gameState.runStatelessGame(games.StraightColorWave.randomInstance())
    elif command == "b":
        # Left-to-right wave superimposed on top-to-bottom wave
        wave1 = games.StraightColorWave(120, start_loc=Point(100, 100), velocity=Vector(500, 0))
        wave2 = games.StraightColorWave(200, start_loc=Point(100, 100), velocity=Vector(0, 400))
        gameState.runStatelessGame(wave1)
        gameState.runStatelessGame(wave2)
    elif command == "c":
        # A randomized circular wave
        gameState.runStatelessGame(games.CircularColorWave.randomInstance())
    elif command == "f":
        gameState.runStatefulGame(games.Fairy())
    elif command == "i":
        gameState.runStatefulGame(games.RandomIdle())
    elif command == "s":
        gameState.runStatefulGame(games.WholeFieldSleep())

input_thread = KeyboardInputThread(handle_keyboard_input)

# Interaction/game loop
while True:
    # Update the current set of stateful games
    gameState.updateStatefulGames()

    # Check for any mqtt messages, and send any buffered outgoing messages
    if not mqtt_client.is_connected():
        mqtt_client.reconnect()
    mqtt_client.loop()

    # Stall the loop.
    time.sleep(1/60)  # seconds
