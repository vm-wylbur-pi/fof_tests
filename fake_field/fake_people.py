from dataclasses import dataclass
import json

import paho.mqtt.client as mqtt
import pygame

@dataclass
class Person():
    name: str
    x: int
    y: int

    def draw(self, screen: pygame.Surface):
        face = pygame.Vector2(self.x, self.y)
        chest = pygame.Vector2(self.x, self.y+10)
        crotch = pygame.Vector2(self.x, self.y+20)
        right_hand = pygame.Vector2(self.x+10, self.y)
        left_hand = pygame.Vector2(self.x-10, self.y)
        right_foot = pygame.Vector2(self.x+5, self.y+30)
        left_foot = pygame.Vector2(self.x-5, self.y+30)

        col = pygame.Color("white")
        pygame.draw.circle(screen, col, pygame.Vector2(self.x, self.y), radius=4)  # Head
        pygame.draw.line(screen, col, face, crotch)
        pygame.draw.line(screen, col, chest, right_hand)
        pygame.draw.line(screen, col, chest, left_hand)
        pygame.draw.line(screen, col, crotch, right_foot)
        pygame.draw.line(screen, col, crotch, left_foot)

        # TODO: Consider using text to render person's name.

class FakePeople():
    def __init__(self):
        self.people = []

    def updateLocations(self, mqtt_people_update: mqtt.MQTTMessage):
        people_update_json = mqtt_people_update.payload.decode('utf-8')
        people_update = json.loads(people_update_json)
        # The fake field ignores timestamps. This means it assumes that the message is
        # received very close in time to when the camera module detected the person's location
        # and sent out the update.  The GSA may care more, handling or discarding late-arriving
        # updates.

        # Erase existing person state and recreate from the latest message. The fake field
        # does not do anything for frame-to-frame person coherence.  It just shows what the
        # camera system is sending.
        self.people = []
        for name, location in people_update['people'].items():
            self.people.append(Person(name, location['x'], location['y']))
        #print(f"Recevied locations of {len(self.people)} people.")
    
    def draw(self, screen: pygame.Surface):
        for person in self.people:
            person.draw(screen)

