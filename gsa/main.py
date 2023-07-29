# TODO: docs, what is the GSA?
import time

# Allow absolute import from the root folder. This is needed because
# the GSA prgoram has the non-pythonic structure of putting main.py
# in the same directory as the modules it uses.
if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname
    path.append(dirname(path[0]))


import flower
import field
import person
import mqtt

DEPLOYMENT_FILE = "../fake_field/gsa_testing_deployment.yaml"

# Wrapper for references to the game state.
class GameState:
    def __init__(self):
        self.flowers = flower.readFlowersFromDeploymentYAML(DEPLOYMENT_FILE)
        self.field = field.Field(DEPLOYMENT_FILE)
        self.people = person.People()
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

# Interaction/game loop
while True:
    # Update the current set of stateful games
    gameState.updateStatefulGames()

    # Check for any mqtt messages, and send any buffered outgoing messages
    # This is used for handling
    #  1) game control commands from the FCC to start/end games
    #  2) people location updates from the VA (camera system)
    if not mqtt_client.is_connected():
        mqtt_client.reconnect()
    mqtt_client.loop()

    gameState.people.removePeopleNotSeenForAWhile()

    # Stall the loop.
    time.sleep(1/60)  # seconds
