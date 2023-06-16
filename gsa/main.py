# TODO: docs, what is the GSA?
import time
import threading

import flower
import mqtt
import games
from geometry import Point, Vector

# Wrapper for references to the game state.
class GameState:
    def __init__(self):
        self.flowers = flower.readFieldFromDeploymentYAML(
            "../fake_field/jeffs_living_room_deployment.yaml")
        self.stateful_games = []

    def runStatelessGame(self, game):
        game.run(self.flowers)

    def runStatefulGame(self, game):
        self.stateful_games.append(game)

    def clearStatefulGames(self):
        self.stateful_games = []

    def updateStatefulGames(self):
        self.stateful_games = [g for g in self.stateful_games if not g.isDone()]
        for game in self.stateful_games:
            game.runLoop(self.flowers)

gameState = GameState()
mqtt_client = mqtt.SetupMQTTClient(gameState)

# TODO: There is probably better way to share the mqtt client handle with each flower.
for flower in gameState.flowers:
    flower.mqtt_client = mqtt_client

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
    elif command == "a":
        # A single left-to-right wave
        wave = games.StraightColorWave(120, start_loc=Point(100,100), velocity=Vector(500,0))
        gameState.runStatelessGame(wave)
    elif command == "b":
        # Left-to-right wave superimposed on top-to-bottom wave
        wave1 = games.StraightColorWave(120, start_loc=Point(100, 100), velocity=Vector(500, 0))
        wave2 = games.StraightColorWave(200, start_loc=Point(100, 100), velocity=Vector(0, 400))
        gameState.runStatelessGame(wave1)
        gameState.runStatelessGame(wave2)
    elif command == "c":
        # An expanding circle wave.
        wave = games.CircularColorWave(120, center=Point(400,400), startRadius=0, speed=250)
        gameState.runStatelessGame(wave)

    elif command == "f":
        gameState.runStatefulGame(games.Fairy())

input_thread = KeyboardInputThread(handle_keyboard_input)

# Interaction/game loop
while True:
    # Update the current set of stateful games
    gameState.updateStatefulGames()

    # Check for any mqtt messages, and send any buffered outgoing messages
    if not mqtt_client.is_connected():
        mqtt_client.reconnect()
    mqtt_client.loop()

    # We may want something like this later. For now, the input() call at the top stalls the loop.
    time.sleep(1/60)  # seconds
