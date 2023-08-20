# TODO: docs, what is the GSA?
import time

# Allow absolute import from the root folder. This is needed because
# the GSA prgoram has the non-pythonic structure of putting main.py
# in the same directory as the modules it uses.
if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname
    path.append(dirname(path[0]))

# import sys
# sys.exit()


import mqtt
import game_state

DEPLOYMENT_FILE = "../fake_field/dress_rehearsal_deployment.yaml"

gameState = game_state.GameState(deployment_file=DEPLOYMENT_FILE)
# The mqtt client gets a reference to the game state so that:
#  1) it can pass it on to each flower object. The flower objects each can send
#     mqtt messages to the real-world flowers they represent
#  2) it can be used in the callbacks that respond to person location
#     updates (currently sent over MQTT)
mqtt_client = mqtt.SetupMQTTClient(gameState)
# Starts the MQTT polling loop in a separate thread.
mqtt_client.loop_start()

# Interaction/game loop
while True:
    # Update the current set of stateful games
    gameState.updateStatefulGames()
    gameState.people.removePeopleNotSeenForAWhile()
    gameState.mqttThrottler.resetMessageCount()

    # Stall the loop.
    time.sleep(1/60)  # seconds
