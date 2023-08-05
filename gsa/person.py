from dataclasses import dataclass
import json
import random
import time

import paho.mqtt.client as mqtt

from geometry import Point

# A person in the field.
@dataclass
class Person():
    name: str = ""
    location: Point = None
    last_seen: int = None

class People():
    def __init__(self):
        self.people = {}
        self.last_update = None

    def updateFromMQTT(self, mqtt_people_update: mqtt.MQTTMessage):
        people_update_json = mqtt_people_update.payload.decode('utf-8')
        update = json.loads(people_update_json)
        
        # Skip received-out-of-order (obsolete) updates
        if self.last_update and self.last_update > update['timestamp']:
            return
        else:
            self.last_update = update['timestamp']

        # Any people *not* included in this update message will be preserved
        # at their prior location.  
        for name, location in update['people'].items():
            person = None
            if name in self.people:
                person = self.people[name]
            else:
                # We've never seen this person before; instantiate them.
                person = Person(name)
                self.people[name] = person
            person.location = Point(location['x'], location['y'])
            person.last_seen = update['timestamp']

    def removePeopleNotSeenForAWhile(self):
        # How much time can pass without seeing a person before they are 
        # considered gone. During the time between when we stop seeing them and
        # they timeout via this mechanism, the games will treat them as stationary
        # in their last known location.
        PERSON_TIMEOUT = 2000  # milliseconds

        # Timestamps in people updates are milliseconds since the unix epoch
        # (in the mock-people code they come from Javascript's Date.now()), so
        # they are comparable with python's time.time().
        now = time.time() * 1000
        for person in list(self.people.keys()):
            time_since_last_seen = now - self.people[person].last_seen
            if time_since_last_seen > PERSON_TIMEOUT:
                print(f"Forgetting about {person}, who hasn't been seen in a while.")
                del self.people[person]

# Class to track the association of colors with people, and assign new colors
# to new people arriving on the field.
class HueAssignments:

    # A set of distinguishable colors, with names for redable debugging messages.
    hueMenu = {
        0: 'red',
        32: 'orange',
        64: 'yellow',
        96: 'green',
        128: 'aqua',
        160: 'blue',
        192: 'purple',
        224: 'pink',
    }

    def __init__(self):
        # Which person has which color. People are their names. Colors are 0-255 hues.
        self.hue_assignments: dict[str, int] = {}

    def hueName(self, hue):
        return HueAssignments.hueMenu.get(hue, "some other random hue")

    def chooseNextHue(self):
        if not self.hue_assignments:
            return random.choice(list(HueAssignments.hueMenu.keys()))
        else:
            remaining_colors = [c for c in HueAssignments.hueMenu.keys()
                                if c not in self.hue_assignments.values()]
            if remaining_colors:
                return random.choice(remaining_colors)
            else:
                # This would be a lot of simultaneous people in the field.
                return random.randint(0, 255)

    def updateColorAssignments(self, activePersonNames):
        assignedNames = list(self.hue_assignments.keys())
        for name in assignedNames:
            if name not in activePersonNames:
                del self.hue_assignments[name]
                print(f"Removed hue assignment from {name}.")

        for name in activePersonNames:
            if name not in self.hue_assignments:
                self.hue_assignments[name] = self.chooseNextHue()
                print(
                    f"Assigned hue {self.hue_assignments[name]} to {name}.")

    def getAssignment(self, name: str) -> int:
        if name not in self.hue_assignments:
            print(
                "WARNING: Requested hue assignment of unknown person. Returning random hue.")
            self.hue_assignments[name] = random.randint(0, 255)
        return self.hue_assignments.get(name, 0)
