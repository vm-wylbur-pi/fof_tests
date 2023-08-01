# This is a python program that is meant to stand in for the field of flowers
# for testing multi-flower effects.
#
# It consists of a graphics window showing a simplified view of the field, in which
# flowers are simple colored circles.  Each flower is represented as a FakeFlower
# instance and is coded to
#   - subscribe to the same MQTT commands that the real flowers receive
#   - render themselves into the graphics window approximating how the real flowers
#     would light up in response to those commands.
#
# It would be a ton of work to re-implement all the flower behavior; the fake flowers
# are very simplified (one color for blossom, one color for leaves). They only support
# a small subset of the commands the actual flowers know how to handle. But it should be
# a good stand-in. We should be able to run the flower coordination program (the GSA)
# and see its effects simultaneously on real flowers and in the fake_field.

import pygame
import paho.mqtt.client as mqtt

import fake_flowers
import fake_people
import mqtt_handling

# Initialize the graphics window in which the fake field is rendered.
pygame.init()
screen = pygame.display.set_mode((1000, 1000))
# Game clock is a global variable also used to stand-in for NTP-synced
# time in each flower. The flowers do still need to handle the control timer
# offset.
clock = pygame.time.Clock()
running = True
FPS = 60

flowers = fake_flowers.makeFakeFieldFromDeploymentYAML("gsa_testing_deployment.yaml")
people = fake_people.FakePeople()

# Pass a handle to the set of flowers and people to the MQTT-handling module, so that
# they can be sent commands and updated when MQTT messages are received from the GSA.
mqtt_client = mqtt_handling.SetupMQTTClient(flowers, people)
# Start the mqtt_client communication loop in a separate thread. This is much easier
# than coordinating the polling with the pygame thread.
mqtt_client.loop_start()

while running:
    # poll for events.  We get events from both the keyboard/mouse, and from MQTT.
    # MQTT events are handled via the callback registered in the receive_mqttt module.
    #
    # pygame.QUIT event means the a click on the close-window GUI widget
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        print("starting hue wave")

    # solid fill to wipe away anything from last frame
    screen.fill("black")
    # TODO: If we add a field boundary rectangle to the deployment config, render it here.

    # Flower rendering. This is dependent on any commands they have received so far.
    for flower in flowers:
        flower.draw(screen)

    # Person rendering.  They will be drawn wherever the most recent update placed them.
    # There's no smoothing applied between locations.
    people.draw(screen)

    # double buffering
    pygame.display.flip()

    # Advance the pygame clock sufficiently to get 60 FPS display.  This will block
    # like sleep(), for however much time is needed so that ticks happen at least
    # 1/FPS seconds appart. It's important to call this last, so that all other work
    # in the game loop (flower rendering, MQTT message handling) can happen before
    # blocking.
    clock.tick(FPS)

pygame.quit()
