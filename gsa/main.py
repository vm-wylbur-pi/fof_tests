# TODO: docs, what is the GSA?

import flower
import mqtt
import games
from geometry import Point, Vector

mqtt_client = mqtt.SetupMQTTClient()

flowers = flower.readFieldFromDeploymentYAML("../fake_field/test_deployment.yaml")

# TODO: There is probably better way to share the mqtt client handle
for flower in flowers:
    flower.mqtt_client = mqtt_client

# Interaction/game loop
while True:
    # at first, keyboard control.  This will generalize to received MQTT commands later.
    command = input("Next command? ")
    if command == "a":
        # A single left-to-right wave
        games.StraightColorWave(120, start_loc=Point(100,100), velocity=Vector(500,0)).run(flowers)
    elif command == "b":
        # Left-to-right wave superimposed on top-to-bottom wave
        games.StraightColorWave(120, start_loc=Point(100, 100), velocity=Vector(500, 0)).run(flowers)
        games.StraightColorWave(200, start_loc=Point(100, 100), velocity=Vector(0, 400)).run(flowers)


    # Check for any mqtt messages, and send any buffered outgoing messages
    if not mqtt_client.is_connected():
        mqtt_client.reconnect()
    mqtt_client.loop()

